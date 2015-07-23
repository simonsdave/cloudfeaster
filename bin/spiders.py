#!/usr/bin/env python

import json

import cloudfeaster.spider
import importlib
import logging
import optparse
import os
import pip
import pkgutil
import time

_logger = logging.getLogger(__name__)


class CommandLineParser(optparse.OptionParser):

    def __init__(self):
        description = (
            "Utility to discover all spiders and thier associated metadata."
        )
        optparse.OptionParser.__init__(
            self,
            "usage: %prog [options] <package>",
            description=description)

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        if 0 != len(cla):
            self.error("try again ...")
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
    spiders = {}
    for i in pip.get_installed_distributions():
        if not i.key.endswith("-spiders"):
            continue

        spider_package_name = i.egg_name()[:-len("-%s-py%s" % (i.version, i.py_version))]

        spider_package = importlib.import_module(spider_package_name)

        spider_package_dir_name = os.path.dirname(spider_package.__file__)

        for (module_loader, name, ispkg) in pkgutil.iter_modules([spider_package_dir_name]):
            importlib.import_module(spider_package_name + "." + name)

    for spider_class in cloudfeaster.spider.Spider.__subclasses__():
        full_spider_name = spider_class.__module__ + "." + spider_class.__name__
        spiders[full_spider_name] = spider_class.get_validated_metadata()

    print json.dumps(spiders)
