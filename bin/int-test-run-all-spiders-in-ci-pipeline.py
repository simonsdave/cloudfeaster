#!/usr/bin/env python3.9
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
#   ~> docker run \
#       --rm \
#       -it \
#       -v /var/run/docker.sock:/var/run/docker.sock \
#       -v $(repo-root-dir.sh):/app \
#       ${DEV_ENV_DOCKER_IMAGE} \
#       /bin/bash
#   root@fb740b14ab66:/app# int-test-run-all-spiders-in-ci-pipeline.py \
#       --max-num-spiders-to-run 1 \
#       --max-num-seconds-spiders-run 30 \
#       --log=info \
#       /app/dave \
#       simonsdave/gaming-spiders:bindle
#

import datetime
import json
import logging
import optparse
import os
import re
import sys
import subprocess
import time

import dateutil.parser

import cloudfeaster

_logger = logging.getLogger(__name__)


def _check_logging_level(option, opt, value):
    """Type checking function for command line parser's 'logginglevel' type."""
    reg_ex_pattern = "^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
    if reg_ex.match(value):
        return getattr(logging, value.upper())
    fmt = (
        "option %s: should be one of "
        "DEBUG, INFO, WARNING, ERROR or CRITICAL"
    )
    raise optparse.OptionValueError(fmt % opt)


class CommandLineOption(optparse.Option):
    """Adds new option types to the command line parser's base option types."""
    new_types = (
        'logginglevel',
    )
    TYPES = optparse.Option.TYPES + new_types
    TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
    TYPE_CHECKER['logginglevel'] = _check_logging_level


class CommandLineParser(optparse.OptionParser):

    def __init__(self):

        optparse.OptionParser.__init__(
            self,
            'usage: %prog [options] <output-dir> <docker-image>',
            description='discover spiders',
            version='%%prog %s' % cloudfeaster.__version__,
            option_class=CommandLineOption)

        default = 1
        fmt = '# spiders to run @ same time - default = {default}'
        help = fmt.format(default=default)
        self.add_option(
            '--max-num-spiders-to-run',
            action='store',
            type='int',
            dest='max_number_spiders_to_run',
            default=default,
            help=help)

        default = 60
        fmt = 'max # seconds to run spider - default = {default}'
        help = fmt.format(default=default)
        self.add_option(
            '--max-num-seconds-spiders-run',
            action='store',
            type='int',
            dest='max_seconds_spiders_to_run',
            default=default,
            help=help)

        default = logging.ERROR
        fmt = (
            "logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL] - "
            "default = %s"
        )
        help = fmt % logging.getLevelName(default)
        self.add_option(
            "--log",
            action="store",
            dest="logging_level",
            default=default,
            type="logginglevel",
            help=help)

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        if len(cla) != 2:
            self.error('output dir & docker image are required')

        return (clo, cla)


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

        all_the_metadata = json.loads(subprocess.check_output(args).decode('UTF-8').strip())
        del all_the_metadata['_metadata']

        filenames_by_spider_name = {}

        for (category, spiders) in all_the_metadata.items():
            for (name, metadata) in spiders.items():
                filenames_by_spider_name[name] = metadata['absoluteFilename']

        return filenames_by_spider_name


class CrawlContainer(object):

    def __init__(self, spider, absolute_filename, docker_image):
        object.__init__(self)

        self.spider = spider
        self.absolute_filename = absolute_filename
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
            self.absolute_filename,
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
        spider_output_dir = os.path.join(
            output_dir,
            self.spider)
        # os.makedirs() will throw an exception if there's an error
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
    #
    # parse command line
    #
    clp = CommandLineParser()
    (clo, cla) = clp.parse_args()

    (output_dir, docker_image) = cla

    #
    # configure logging ... remember gmt = utc
    #
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        level=clo.logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s')

    #
    # Useful for debugging
    #
    _logger.info('Output >>>{output_dir}<<<'.format(output_dir=output_dir))
    _logger.info('Docker image >>>{docker_image}<<<'.format(docker_image=docker_image))
    _logger.info('Max # spider to run >>>{max_num_spiders}<<<'.format(max_num_spiders=clo.max_number_spiders_to_run))
    msg = 'Max # seconds for spider to run >>>{max_num_seconds}<<<'.format(
        max_num_seconds=clo.max_seconds_spiders_to_run)
    _logger.info(msg)

    #
    # now the real work begins ...
    #
    filenames_by_spider_name = SpidersContainer(docker_image).spiders()

    spiders_left_to_run = list(filenames_by_spider_name.keys())

    running_spiders = []
    run_spiders = []

    _logger.info('Spiders to run {spiders}'.format(spiders=spiders_left_to_run))

    while spiders_left_to_run or running_spiders:
        # check if any of the running spiders have finished
        for running_spider in running_spiders:
            if running_spider.is_finished():
                msg = '>>>{spider}<<< finished running - {status}'.format(
                    spider=running_spider.spider,
                    status='success' if running_spider.is_success() else 'failure')
                _logger.info(msg)
                running_spider.save_output(output_dir)

                running_spiders.remove(running_spider)
                run_spiders.append(running_spider)
            else:
                number_seconds_running = running_spider.number_seconds_running()

                if clo.max_seconds_spiders_to_run < number_seconds_running:
                    msg_fmt = (
                        '>>>{spider}<<< ran for {seconds:.0f} '
                        'seconds which is too long (> {max} seconds) - killing spider'
                    )
                    msg = msg_fmt.format(
                        spider=running_spider.spider,
                        seconds=number_seconds_running,
                        max=clo.max_seconds_spiders_to_run)
                    _logger.info(msg)

                    running_spider.kill()
                    running_spider.save_output(
                        output_dir,
                        {'_metadata': {'status': {'code': 400, 'message': 'spider took too long to run'}}})

                    running_spiders.remove(running_spider)
                    run_spiders.append(running_spider)
                else:
                    msg = '>>>{spider}<<< still running after {seconds:.0f} seconds'.format(
                        spider=running_spider.spider,
                        seconds=number_seconds_running)
                    _logger.info(msg)

        # start spiders left to run until max # of spiders running reached
        while spiders_left_to_run:
            if len(running_spiders) < clo.max_number_spiders_to_run:
                spider = spiders_left_to_run.pop(0)
                cc = CrawlContainer(spider, filenames_by_spider_name[spider], docker_image)
                cc.start()
                running_spiders.append(cc)
                _logger.info('>>>{spider}<<< started running'.format(spider=spider))
            else:
                break

        time.sleep(1)

    sys.exit(0)
