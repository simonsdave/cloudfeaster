#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

#
# A spider CI pipeline builds a docker image containing spiders.
# Ideally the CI pipeline would run each of the spiders in the
# docker image ala the way the spider will be run in production.
#
# int-test-run-all-spiders-in-ci-pipeline.py runs spiders.py
# to discover all spiders in a docker image and then spins up
# a docker container to run each spider.
#
# Command line usage
#
#   int-test-run-all-spiders-in-ci-pipeline.py
#       <#-spiders-2-run-at-same-time>
#       <max-secs-for-spider-to-run>
#       <output-dir>
#       <docker-image>
#
# Note re <#-spiders-2-run-at-same-time> - from trial and error
# it seems as though only a single spider can be run reliably.
# Assumption is that this is some kind of resource constraint.
#
# When developing spiders it's useful to be able to test all
# spiders. To do this start a docker image per below and run
# int-test-run-all-spiders-in-ci-pipeline.py once the shell
# is running in the container.
#
#   docker run \
#      --rm \
#      -it \
#      -v /var/run/docker.sock:/var/run/docker.sock \
#      -v $(repo-root-dir.sh):/app \
#      ${DEV_ENV_DOCKER_IMAGE} \
#      /bin/bash
#

import datetime
import json
import os
import sys
import subprocess
import time

import dateutil.parser


class SpidersContainer(object):

    def __init__(self, docker_image):
        object.__init__(self)

        self.docker_image = docker_image

    def spiders(self):
        args = [
            'docker',
            'run',
            self.docker_image,
            'spiders.py',
        ]

        output = json.loads(subprocess.check_output(args).decode('UTF-8').strip())

        rv = list(output.keys())
        rv.remove('_metadata')
        rv.sort()

        return rv


class CrawlContainer(object):

    def __init__(self, spider, docker_image):
        object.__init__(self)

        self.spider = spider
        self.docker_image = docker_image

        self.container_id = None

    def start(self):
        if self.container_id:
            return None

        args = [
            'docker',
            'run',
            '-d',
            self.docker_image,
            self.spider,
        ]
        self.container_id = subprocess.check_output(args).decode('UTF-8').strip()

        return self.container_id

    def is_finished(self):
        if not self.container_id:
            return False

        args = [
            'docker',
            'inspect',
            self.container_id,
        ]
        status = json.loads(subprocess.check_output(args).decode('UTF-8').strip())[0]['State']['Status']
        return status != 'running'

    def kill(self):
        if not self.container_id:
            return False

        args = [
            'docker',
            'kill',
            self.container_id,
        ]
        subprocess.check_output(args)

        return True

    def output(self):
        if not self.is_finished():
            return None

        args = [
            'docker',
            'logs',
            self.container_id,
        ]
        return json.loads(subprocess.check_output(args).decode('UTF-8').strip())

    def is_success(self):
        if not self.is_finished():
            return False

        return self.output()['_metadata']['status']['code'] == 0

    def number_seconds_running(self):
        if not self.container_id:
            return None

        args = [
            'docker',
            'container',
            'inspect',
            self.container_id,
        ]
        start_date_as_str = json.loads(subprocess.check_output(args).decode('UTF-8').strip())[0]['State']['StartedAt']
        start_date = dateutil.parser.parse(start_date_as_str)
        now = datetime.datetime.utcnow().replace(tzinfo=start_date.tzinfo)
        return (now - start_date).total_seconds()

    def save_output(self, output_dir, output=None):
        spider_output_dir = os.path.join(output_dir, os.path.splitext(self.spider)[0])
        os.makedirs(spider_output_dir)

        if not output:
            output = self.output()
            if not output:
                return

        self._copy_debug_file(output, 'screenshot', spider_output_dir, 'screenshot.png')
        self._copy_debug_file(output, 'crawlLog', spider_output_dir, 'crawl-log.txt')
        self._copy_debug_file(output, 'chromeDriverLog', spider_output_dir, 'chrome-driver-log.txt')

        with open(os.path.join(spider_output_dir, 'crawl-output.json'), 'w', encoding='utf8') as f:
            json.dump(output, f, ensure_ascii=False)

    def _copy_debug_file(self, output, debug_file_property, spider_output_dir, debug_filename):
        filename_in_docker_container = output.get('_debug', {}).get(debug_file_property, None)
        if not filename_in_docker_container:
            return None

        args = [
            'docker',
            'container',
            'cp',
            '{container_id}:{filename_in_docker_container}'.format(
                container_id=self.container_id,
                filename_in_docker_container=filename_in_docker_container),
            os.path.join(spider_output_dir, debug_filename),
        ]
        subprocess.check_output(args)

        output['_debug'][debug_file_property] = debug_filename


if __name__ == "__main__":
    if len(sys.argv) != 5:
        fmt = "usage: {app} <#-spiders-2-run-at-same-time> <max-secs-for-spider-to-run> <output-dir> <docker-image>"
        print(fmt.format(app=os.path.split(sys.argv[0])[1]))
        sys.exit(1)

    max_number_spiders_to_run = int(sys.argv[1])
    max_seconds_spiders_to_run = int(sys.argv[2])
    output_dir = sys.argv[3]
    docker_image = sys.argv[4]

    spiders_left_to_run = SpidersContainer(docker_image).spiders()

    running_spiders = []
    run_spiders = []

    while spiders_left_to_run or running_spiders:
        # check if any of the running spiders have finished
        for running_spider in running_spiders:
            if running_spider.is_finished():
                print('>>>{spider}<<< finished running - {status}'.format(
                    spider=running_spider.spider,
                    status='success' if running_spider.is_success() else 'failure'))
                running_spider.save_output(output_dir)

                running_spiders.remove(running_spider)
                run_spiders.append(running_spider)
            else:
                number_seconds_running = running_spider.number_seconds_running()

                if max_seconds_spiders_to_run < number_seconds_running:
                    msg_fmt = (
                        '>>>{spider}<<< ran for {seconds:.0f} '
                        'seconds which is too long (> {max} seconds) - killing spider'
                    )
                    print(msg_fmt.format(
                        spider=running_spider.spider,
                        seconds=number_seconds_running,
                        max=max_seconds_spiders_to_run))

                    running_spider.kill()
                    running_spider.save_output(
                        output_dir,
                        {'_metadata': {'status': {'code': 400, 'message': 'spider took too long to run'}}})

                    running_spiders.remove(running_spider)
                    run_spiders.append(running_spider)
                else:
                    print('>>>{spider}<<< still running after {seconds:.0f} seconds'.format(
                        spider=running_spider.spider,
                        seconds=number_seconds_running))

        # start spiders left to run until max # of spiders running reached
        while spiders_left_to_run:
            if len(running_spiders) < max_number_spiders_to_run:
                spider = spiders_left_to_run.pop(0)
                cc = CrawlContainer(spider, docker_image)
                cc.start()
                running_spiders.append(cc)
                print('>>>{spider}<<< started running'.format(spider=spider))
            else:
                break

        time.sleep(1)

    sys.exit(0)
