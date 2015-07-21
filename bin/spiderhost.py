#!/usr/bin/env python

import importlib
import json
import logging
import optparse
import time
import urlparse

from cloudfeaster.spider import SpiderCrawler

_logger = logging.getLogger(__name__)


def parse_spider_args_option(option, opt, full_spider_class_name):
    """load the spider module+class as specified by name
    on the command line.
    """
    # :QUESTION: are we trying to do too much in this one function?
    try:
        split_full_spider_class_name = full_spider_class_name.split(".")
        spider_module_name = ".".join(split_full_spider_class_name[:-1])
        spider_class_name = split_full_spider_class_name[-1]
        spider_module = importlib.import_module(spider_module_name)
        spider_class = getattr(spider_module, spider_class_name)
        return spider_class
    except Exception as ex:
        msg = "option %s: unknown spider '%s' - detail = %s" % (
            opt,
            full_spider_class_name,
            ex.message)
        raise optparse.OptionValueError(msg)


def parse_urlencoded_spider_args_option(option, opt, value):
    """...
    """
    try:
        parsed_value = urlparse.parse_qs(
            value,
            keep_blank_values=True,
            strict_parsing=True)
        return [parsed_value[str(i)][0] for i in range(0, len(parsed_value))]
    except ValueError:
        msg = "option %s: must be url encoded query string" % opt
        raise optparse.OptionValueError(msg)


class CommandLineParserOption(optparse.Option):
    """...
    """
    new_types = (
        "urlencoded_spider_args",
        "spider_arg",
    )
    TYPES = optparse.Option.TYPES + new_types
    TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
    TYPE_CHECKER["urlencoded_spider_args"] = parse_urlencoded_spider_args_option
    TYPE_CHECKER["spider_arg"] = parse_spider_args_option


class CommandLineParser(optparse.OptionParser):

    def __init__(self):
        description = (
            "The Spider Host ..."
        )
        optparse.OptionParser.__init__(
            self,
            "usage: %prog [options]",
            description=description,
            option_class=CommandLineParserOption)

        help = "spider - required"
        self.add_option(
            "--spider",
            action="store",
            dest="spider_class",
            default=None,
            type="spider_arg",
            help=help)

        help = "args - required"
        self.add_option(
            "--args",
            action="store",
            dest="args",
            default=[],
            type="urlencoded_spider_args",
            help=help)

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        if not clo.spider_class:
            self.error("'--spider' is required")
        return (clo, cla)


if __name__ == "__main__":
    #
    # parse the command line ...
    #
    clp = CommandLineParser()
    (clo, cla) = clp.parse_args()

    #
    # configure logging ...
    #
    # remember gmt = utc
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y-%m-%dT%H:%M:%S",
        format="%(asctime)s.%(msecs)03d+00:00 %(process)d "
        "%(levelname)5s %(module)s:%(lineno)d %(message)s")

    #
    # Run the spider and dump results to stdout
    #
    spider_crawler = SpiderCrawler(clo.spider_class)
    crawl_result = spider_crawler.crawl(*clo.args)
    print json.dumps(crawl_result)
