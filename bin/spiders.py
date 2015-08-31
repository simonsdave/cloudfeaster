#!/usr/bin/env python

import json

import cloudfeaster.spider
import importlib
import logging
import optparse
import os
import pip
import pkgutil
import re
import time

_logger = logging.getLogger(__name__)


#
# egg_name_reg_ex is used to extract module names from egg_names
# like ```gaming_spiders-0.1.0-py2.7```.
#
_egg_name_reg_ex = re.compile(
    "^\s*(?P<egg_name>.+spiders)-\d+\.\d+\.\d+\-py\d+\.\d+\s*$",
    re.IGNORECASE)


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
        match = _egg_name_reg_ex.match(i.egg_name())
        if not match:
            continue

        spider_package_name = match.group("egg_name")

        spider_package = importlib.import_module(spider_package_name)

        spider_package_dir_name = os.path.dirname(spider_package.__file__)

        for (module_loader, name, ispkg) in pkgutil.iter_modules([spider_package_dir_name]):
            importlib.import_module(spider_package_name + "." + name)

    for spider_class in cloudfeaster.spider.Spider.__subclasses__():
        full_spider_name = spider_class.__module__ + "." + spider_class.__name__
        spiders[full_spider_name] = spider_class.get_validated_metadata()

    print json.dumps(spiders)
