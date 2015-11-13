#!/usr/bin/env python

import json
import logging
import optparse
import time
import urlparse

from cloudfeaster.spider import SpiderCrawler


def parse_urlencoded_spider_args_option(option, opt, value):
    if not value:
        # since urlparse.parse_qs() fails on zero length string
        return []
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
    new_types = (
        "urlencoded_spider_args",
    )
    TYPES = optparse.Option.TYPES + new_types
    TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
    TYPE_CHECKER["urlencoded_spider_args"] = parse_urlencoded_spider_args_option


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
            dest="spider",
            default=None,
            type="string",
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
        if not clo.spider:
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
    spider_crawler = SpiderCrawler(clo.spider)
    crawl_result = spider_crawler.crawl(*clo.args)
    print json.dumps(crawl_result)
