#!/usr/bin/env python

import json
import logging
import optparse
import re
import time

from cloudfeaster.spider import SpiderCrawler
from cloudfeaster import webdriver_spider


def _check_logging_level(option, opt, value):
    """Type checking function for command line parser's 'logginglevel' type."""
    reg_ex_pattern = "^(DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL)$"
    reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
    if reg_ex.match(value):
        return getattr(logging, value.upper())
    fmt = (
        "option %s: should be one of "
        "DEBUG, INFO, WARNING, ERROR, CRITICAL or FATAL"
    )
    raise optparse.OptionValueError(fmt % opt)


def _check_host_colon_port(option, opt, value):
    """Type checking function for command line parser's
    'hostcolonport' type.
    """
    reg_ex_pattern = '^(?P<host>[^\:]+)\:(?P<port>\d+)$'
    reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
    match = reg_ex.match(value)
    if not match:
        msg = 'option %s: required format is host:port' % opt
        raise optparse.OptionValueError(msg)
    return (match.group('host'), int(match.group('port')))


class CommandLineOption(optparse.Option):
    """Adds new option types to the command line parser's base
    option types.
    """
    new_types = (
        'logginglevel',
        'hostcolonport',
    )
    TYPES = optparse.Option.TYPES + new_types
    TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
    TYPE_CHECKER['logginglevel'] = _check_logging_level
    TYPE_CHECKER['hostcolonport'] = _check_host_colon_port


class CommandLineParser(optparse.OptionParser):

    def __init__(self):
        optparse.OptionParser.__init__(self)

        description = (
            'spider hosts accept the name of a spider, '
            'the arguments to run the spider and optionally '
            'proxy server details. armed with all this info '
            'the spider host runs a spider and dumps the '
            'result to stdout.'
        )
        optparse.OptionParser.__init__(
            self,
            'usage: %prog <spider> [<arg1> ... <argN>]',
            description=description,
            option_class=CommandLineOption)

        self.spider = None
        self.args = None

        default = logging.ERROR
        fmt = (
            "logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - "
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

        default = None
        help = 'proxy host:port - default = %s' % default
        self.add_option(
            '--proxy',
            action='store',
            dest='proxy',
            default=default,
            type='hostcolonport',
            help=help)

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        if not cla:
            self.error('spider is required')

        self.spider = cla[0]
        self.args = cla[1:]

        return (clo, cla)


if __name__ == '__main__':
    #
    # parse the command line ...
    #
    clp = CommandLineParser()
    (clo, cla) = clp.parse_args()

    #
    # configure logging ...
    #
    # remember gmt = utc
    #
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        level=clo.logging_level,
        datefmt='%Y-%m-%dT%H:%M:%S',
        format='%(asctime)s.%(msecs)03d+00:00 %(process)d '
        '%(levelname)5s %(module)s:%(lineno)d %(message)s')

    #
    # proxy configuration
    #
    if clo.proxy:
        (webdriver_spider.proxy_host, webdriver_spider.proxy_port) = clo.proxy

    #
    # Run the spider, log metrics and dump results to stdout
    #
    spider_crawler = SpiderCrawler(clp.spider)
    crawl_result = spider_crawler.crawl(*clp.args)

    print json.dumps(crawl_result)
