#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import sys


_prefix = """---
version: 2.1

executors:
  dev-env:
    docker:
      - image: simonsdave/cloudfeaster-xenial-dev-env:v{cloudfeaster_version}

jobs:
  build_test_and_package:
    working_directory: ~/repo
    executor: dev-env
    steps:
      - checkout
      - run: check-consistent-clf-version.sh --verbose
      - run: check-circleci-config.sh
      - restore_cache:
          keys:
            - v1-dependencies-{{{{ checksum "requirements.txt" }}}}
            - v1-dependencies-
      - run:
          name: Install Python prerequisites
          command: pip install --requirement requirements.txt
      - save_cache:
          paths:
            - ./env
          key: v1-dependencies-{{{{ checksum "requirements.txt" }}}}
      - run: run-pip-check.sh
      - run:
          name: Lint Python Files
          command: run-flake8.sh
      - run:
          name: PyCQA/bandit
          command: run-bandit.sh
      - run:
          name: Lint Shell Scripts
          command: run-shellcheck.sh
      - run:
          name: Lint YAML Files
          command: run-yamllint.sh
      - run:
          name: Scan repo for passwords, private keys, etc.
          command: run-repo-security-scanner.sh
      - run:
          name: Snyk vulnerability assessment
          command: run-snyk.sh "$SNYK_TOKEN"
      - run:
          name: Run unit tests
          command: run-unit-tests.sh
      - run:
          name: Build python packages
          command: build-python-package.sh
      - persist_to_workspace:
          root: dist
          paths:
            - {package}-*.whl
            - {package}-*.tar.gz
  run_spider:
    executor: dev-env
    parameters:
      spider:
        type: string
    steps:
      - attach_workspace:
          at: dist
      - run:
          name: spider install from dist
          command: pip install dist/{package}*.tar.gz
      - run:
          name: run spider
          command: << parameters.spider >>.py
  save_artifacts:
    executor: dev-env
    steps:
      - attach_workspace:
          at: dist
      - store_artifacts:
          path: dist
          destination: dist

workflows:
  version: 2
  commit:
    jobs:
      - build_test_and_package:
          context: {context}"""


_run_spider_workflow = """      - run_spider:
          spider: {spider}
          name: run_spider_{spider}
          requires:
            - build_test_and_package"""


_save_artifacts_workflow = """      - save_artifacts:
          requires:"""


_save_artifacts_spider = """            - run_spider_{spider}"""

_nightly = """  nightly:
    triggers:
      - schedule:
          cron: "0 0 * * *"
          filters:
            branches:
              only:
                - master
    jobs:
      - build_test_and_package:
          context: {context}"""


def _is_spider_file(spiders_dir, f):
    abs_f = os.path.join(spiders_dir, f)
    return abs_f.endswith('.py') and os.path.isfile(abs_f) and os.access(abs_f, os.X_OK)


def _spider_names(repo_root_dir, package):
    spiders_dir = os.path.join(repo_root_dir, package)
    split_spider_filenames = [os.path.splitext(f) for f in os.listdir(spiders_dir) if _is_spider_file(spiders_dir, f)]
    spider_names = [spider_name for (spider_name, _) in split_spider_filenames]
    spider_names.sort()
    return spider_names


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


if __name__ == "__main__":
    repo_root_dir = subprocess.check_output(['repo-root-dir.sh']).strip()
    repo = subprocess.check_output(['repo.sh']).strip()
    context = repo
    package = repo.replace('-', '_')
    spider_names = _spider_names(repo_root_dir, package)

    data = {
        'package': package,
        'context': context,
        'cloudfeaster_version': _cloudfeaster_version(repo_root_dir),
    }
    print _prefix.format(**data)

    for spider_name in spider_names:
        data = {
            'spider': spider_name,
        }
        print _run_spider_workflow.format(**data)

    print _save_artifacts_workflow

    for spider_name in spider_names:
        data = {
            'spider': spider_name,
        }
        print _save_artifacts_spider.format(**data)

    data = {
        'package': package,
        'context': context,
    }
    print _nightly.format(**data)

    for spider_name in spider_names:
        data = {
            'spider': spider_name,
        }
        print _run_spider_workflow.format(**data)

    print _save_artifacts_workflow

    for spider_name in spider_names:
        data = {
            'spider': spider_name,
        }
        print _save_artifacts_spider.format(**data)

    sys.exit(0)
