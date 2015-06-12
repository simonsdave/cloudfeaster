#!/usr/bin/env python

import importlib
import json
import logging
import optparse
import time

from cloudfeaster.spider import SpiderCrawler

_logger = logging.getLogger(__name__)


class CommandLineParser(optparse.OptionParser):

    def __init__(self):
        description = (
            "The Spider Host ..."
        )
        optparse.OptionParser.__init__(
            self,
            "usage: %prog [options]",
            description=description)

        default = "spiders.spider.Spider"
        help = "spider - default = %s" % default
        self.add_option(
            "--spider",
            action="store",
            dest="full_spider_class_name",
            default=default,
            type="string",
            help=help)

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        # :TODO: force spider argument to be required
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
    # load the spider module+class as specified by name
    # on the command line
    #
    split_full_spider_class_name = clo.full_spider_class_name.split(".")
    spider_module_name = ".".join(split_full_spider_class_name[:-1])
    spider_class_name = split_full_spider_class_name[-1]
    spider_module = importlib.import_module(spider_module_name)
    spider_class = getattr(spider_module, spider_class_name)

    #
    #
    #
    spider_crawler = SpiderCrawler(spider_class)
    crawl_result = spider_crawler.crawl(*cla)

    #
    #
    #
    print json.dumps(crawl_result)
