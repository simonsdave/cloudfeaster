#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import sys


_prefix = """---
version: 2.1

executors:
  my_executor:
    docker:
      - image: {docker_user}/cloudfeaster-dev-env:v{cloudfeaster_version}
        auth:
          username: $DOCKER_EXECUTOR_DOCKERHUB_USERNAME
          password: $DOCKER_EXECUTOR_DOCKERHUB_PASSWORD

commands:
  my_setup_remote_docker:
    steps:
      - setup_remote_docker:
          version: 19.03.13
  test_docker_image:
    parameters:
      docker_image:
        type: string
      # crawl_output_dir is a parameter only because this value is shared
      # across stesp and commands can't have environment variables
      crawl_output_dir:
        default: "/tmp/crawl-output"
        type: string
      # crawl_output_zip_file is a parameter only because this value is shared
      # across stesp and commands can't have environment variables
      crawl_output_zip_file:
        default: "/tmp/crawl-output.zip"
        type: string
    steps:
      - run:
          name: Test Docker Image
          command: |
            #
            # https://support.circleci.com/hc/en-us/articles/360019182513-Build-a-Docker-image-in-one-job-and-use-it-in-another-job
            # https://discuss.circleci.com/t/can-docker-images-be-preserved-between-jobs-in-a-workflow-without-a-manual-load-save/23388
            #
            int-test-run-all-spiders-in-ci-pipeline.py \\
              --max-num-spiders-to-run 1 \\
              --max-num-seconds-spiders-run 60 \\
              --log=info \\
              << parameters.crawl_output_dir >> \\
              << parameters.docker_image >>

            pushd "<< parameters.crawl_output_dir >>"; zip -r "<< parameters.crawl_output_zip_file >>" .; popd
      - store_artifacts:
          # :BUG'ish: should be able to use environment variable
          # on the path since the filename is shared between this step
          # and the preivous one but CI pipeline didn't seem to replace
          # the path's value when it was an environment variable
          path: << parameters.crawl_output_zip_file >>
          destination: crawl-output.zip
      - run:
          name: fail workflow if crawl failed
          command: |
            #
            # we force the "Test Docker Image" step to succeed regardless of
            # the success/failure of a particular spider's crawl. However, we
            # actually want the workflow to fail if any spider's crawl fails
            # and we want to store artifacts before failing the workflow because
            # those artifacts will be used to debug a failed crawl. this is all
            # to explain the need for this somewhat might feel like odd commands
            # below.
            #
            for CRAWL_OUTPUT_DOT_JSON in $(find "<< parameters.crawl_output_dir >>" -name crawl-output.json); do
                if [[ "$(jq ._metadata.status.code "${{CRAWL_OUTPUT_DOT_JSON}}")" != "0" ]]; then
                    echo "Found failure in ${{CRAWL_OUTPUT_DOT_JSON}}"
                    false
                fi
            done

jobs:
  build_package_test_and_deploy:
    working_directory: ~/repo
    executor: my_executor
    environment:
      DOCKER_TEMP_IMAGE: {docker_user}/{repo}:bindle
    steps:
      - checkout
      - run: check-consistent-clf-version.sh --verbose
      - run: check-circleci-config.sh
      - restore_cache:
          keys:
            - v1-dependencies-{{{{ checksum "setup.py" }}}}
            - v1-dependencies-
      - run:
          name: Install Python prerequisites
          command: python3.9 setup.py install
      - save_cache:
          paths:
            - ./env
          key: v1-dependencies-{{{{ checksum "setup.py" }}}}
      - run:
          name: Run pip check
          command: run-pip-check.sh
      - run:
          name: Lint Python Files
          command: run-flake8.sh
      - run:
          name: PyCQA/bandit
          command: run-bandit.sh
      - run:
          name: Lint Shell Scripts
          command: run-shelllint.sh --verbose
      - run:
          name: Lint Markdown Files
          command: run-markdownlint.sh --verbose
      - run:
          name: Lint YAML Files
          command: run-yamllint.sh --verbose
      - run:
          name: Lint JSON Files
          command: run-jsonlint.sh --verbose
      - run:
          name: Scan repo for passwords, private keys, etc.
          command: run-repo-security-scanner.sh
      - run:
          name: Run unit tests
          command: run-unit-tests.sh
      - run:
          name: Build README.rst
          command: build-readme-dot-rst.sh
      - run:
          name: Build python packages
          command: build-python-package.sh
      - store_artifacts:
          path: dist
          destination: dist
      - my_setup_remote_docker
      - run:
          name: Build Docker Image
          command: |
            dockerfiles/build-docker-image.sh \\
              "dist/{package}-$(python-version.sh).tar.gz" \\
              "${{DOCKER_TEMP_IMAGE}}"
      - test_docker_image:
          docker_image: "${{DOCKER_TEMP_IMAGE}}"
      - deploy:
          name: Push docker image to dockerhub
          command: |
            if [[ "${{CIRCLE_BRANCH}}" == "master" ]]; then
              dockerfiles/tag-and-push-docker-image.sh \\
                "${{DOCKER_TEMP_IMAGE}}" \\
                "latest" \\
                "${{DOCKER_PASSWORD}}"
            fi
            if [[ "${{CIRCLE_BRANCH}}" =~ ^release-([0-9]+.)*[0-9]+$ ]]; then
              dockerfiles/tag-and-push-docker-image.sh \\
                "${{DOCKER_TEMP_IMAGE}}" \\
                "v${{CIRCLE_BRANCH##release-}}" \\
                "${{DOCKER_PASSWORD}}"
            fi

  pull_and_test:
    working_directory: ~/repo
    executor: my_executor
    environment:
      DOCKER_IMAGE: {docker_user}/{repo}:latest
    steps:
      - checkout
      - my_setup_remote_docker
      - run:
          name: docker pull
          command: docker pull "${{DOCKER_IMAGE}}"
      - test_docker_image:
          docker_image: "${{DOCKER_IMAGE}}"

workflows:
  version: 2
  commit:
    jobs:
      - build_package_test_and_deploy:
          context:
            - {context}
            - docker-executor

  nightly:
    triggers:
      - schedule:
          # https://crontab.guru/ is super useful in decoding the value of the cron key
          cron: "0 0 * * *"
          filters:
            branches:
              only:
                - master
    jobs:
      - pull_and_test:
          context:
            - {context}
            - docker-executor
"""


def _cloudfeaster_version(repo_root_dir):
    with open(os.path.join(repo_root_dir, 'setup.py')) as f:
        lines = f.readlines()

    reg_ex_pattern = r"\s*['\"]cloudfeaster==(?P<version>\d+\.\d+\.\d+)['\"]\s*,?\s*$"
    reg_ex = re.compile(reg_ex_pattern)

    for line in lines:
        match = reg_ex.match(line)
        if match:
            return match.group('version')

    return None


if __name__ == '__main__':
    repo_root_dir = subprocess.check_output(['repo-root-dir.sh']).decode('UTF-8').strip()
    repo = subprocess.check_output(['repo.sh']).decode('UTF-8').strip()
    context = repo
    package = repo.replace('-', '_')

    data = {
        'docker_user': 'simonsdave',
        'repo': repo,
        'package': package,
        'context': context,
        'cloudfeaster_version': _cloudfeaster_version(repo_root_dir),
    }
    # :TRICKY: the 'strip()' below is important so that it doesn't matter
    # where the trailing """ goes
    print(_prefix.strip().format(**data))

    sys.exit(0)
