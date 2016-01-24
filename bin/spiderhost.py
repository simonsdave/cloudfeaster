#!/usr/bin/env python

import json
import logging
import optparse
import time

from cloudfeaster.spider import SpiderCrawler


class CommandLineParser(optparse.OptionParser):

    def __init__(self):
        optparse.OptionParser.__init__(self)

        description = (
            "The Spider Host ..."
        )
        optparse.OptionParser.__init__(
            self,
            "usage: %prog <spider> [<arg1> ... <argN>]",
            description=description)

        self.spider = None
        self.args = None

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        if not cla:
            self.error("spider is required")
        self.spider = cla[0]
        self.args = cla[1:]
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
    #
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        level=logging.INFO,
        datefmt="%Y-%m-%dT%H:%M:%S",
        format="%(asctime)s.%(msecs)03d+00:00 %(process)d "
        "%(levelname)5s %(module)s:%(lineno)d %(message)s")

    #
    # Run the spider and dump results to stdout
    #
    spider_crawler = SpiderCrawler(clp.spider)
    crawl_result = spider_crawler.crawl(*clp.args)
    print json.dumps(crawl_result)
