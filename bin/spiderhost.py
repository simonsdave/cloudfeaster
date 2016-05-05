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


def _check_a_colon_b(option, opt, value, usage):
    """Type checking function for command line parser's
    types that have the format a:b.
    """
    reg_ex_pattern = '^(?P<a>[^\:]+)\:(?P<b>.+)$'
    reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
    match = reg_ex.match(value)
    if not match:
        msg = 'option %s: required format is %s' % (opt, usage)
        raise optparse.OptionValueError(msg)
    return (match.group("a"), match.group("b"))


def _check_host_colon_port(option, opt, value):
    """Type checking function for command line parser's
    'hostcolonport' type.
    """
    return _check_a_colon_b(option, opt, value, 'host:port')


def _check_user_colon_password(option, opt, value):
    """Type checking function for command line parser's
    'usercolonpassword' type.
    """
    return _check_a_colon_b(option, opt, value, 'user:password')


class CommandLineOption(optparse.Option):
    """Adds new option types to the command line parser's base
    option types.
    """
    new_types = (
        'logginglevel',
        'hostcolonport',
        'usercolonpassword',
    )
    TYPES = optparse.Option.TYPES + new_types
    TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
    TYPE_CHECKER['logginglevel'] = _check_logging_level
    TYPE_CHECKER['hostcolonport'] = _check_host_colon_port
    TYPE_CHECKER['usercolonpassword'] = _check_user_colon_password


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
        help = 'proxy - default = %s' % default
        self.add_option(
            '--proxy',
            action='store',
            dest='proxy',
            default=default,
            type='hostcolonport',
            help=help)

        default = None
        help = 'proxy-user - default = %s' % default
        self.add_option(
            '--proxy-user',
            action='store',
            dest='proxy_user',
            default=default,
            type='usercolonpassword',
            help=help)

        default = None
        help = 'SignalFX API Token - default = %s' % default
        self.add_option(
            '--sf-api-token',
            action='store',
            dest='sf_api_token',
            default=default,
            type='string',
            help=help)

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        if not cla:
            self.error('spider is required')

        self.spider = cla[0]
        self.args = cla[1:]

        return (clo, cla)


def log_signal_fx_metrics(sf_api_token, crawl_result):
    pass


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
    if clo.proxy_user:
        (webdriver_spider.proxy_username, webdriver_spider.proxy_password) = clo.proxy_user

    #
    # Run the spider, log metrics and dump results to stdout
    #
    spider_crawler = SpiderCrawler(clp.spider)
    crawl_result = spider_crawler.crawl(*clp.args)

    if clo.sf_api_token:
        log_signal_fx_metrics(clo.sf_api_token, crawl_result)

    print json.dumps(crawl_result)
