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
    '^\s*(?P<egg_name>.+spiders)-\d+\.\d+\.\d+\-py\d+\.\d+\s*$',
    re.IGNORECASE)


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


class CommandLineOption(optparse.Option):
    """Adds new option types to the command line parser's base
    option types.
    """
    new_types = (
        'logginglevel',
    )
    TYPES = optparse.Option.TYPES + new_types
    TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
    TYPE_CHECKER['logginglevel'] = _check_logging_level


class CommandLineParser(optparse.OptionParser):

    def __init__(self):
        description = (
            'Utility to discover all spiders and thier associated metadata.'
        )
        optparse.OptionParser.__init__(
            self,
            'usage: %prog [options] <package>',
            description=description,
            option_class=CommandLineOption)

        default = False
        help = 'load sample spiders - default = %s' % default
        self.add_option(
            '--samples',
            action='store_true',
            dest='samples',
            default=False,
            help=help)

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

    def parse_args(self, *args, **kwargs):
        (clo, cla) = optparse.OptionParser.parse_args(self, *args, **kwargs)
        if 0 != len(cla):
            self.error('try again ...')
        return (clo, cla)


def _find_concrete_spider_classes(base_class):
    rv = {}
    for sub_class in base_class.__subclasses__():
        if not sub_class.__subclasses__():
            full_spider_class_name = sub_class.__module__ + "." + sub_class.__name__
            rv[full_spider_class_name] = sub_class.get_validated_metadata()
        else:
            rv.update(_find_concrete_spider_classes(sub_class))
    return rv


def _discover_and_load_all_spiders_in_package(spider_package_name):
    spider_package = importlib.import_module(spider_package_name)
    spider_package_dir_name = os.path.dirname(spider_package.__file__)
    _logger.info("looking for spiders in directory '%s'", spider_package_dir_name)
    for (_, name, ispkg) in pkgutil.iter_modules([spider_package_dir_name]):
        if not ispkg:
            module_name = '%s.%s' % (spider_package_name, name)
            _logger.info("attempting to import spider module '%s'", module_name)
            importlib.import_module(module_name)


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
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        level=clo.logging_level,
        datefmt='%Y-%m-%dT%H:%M:%S',
        format='%(asctime)s.%(msecs)03d+00:00 %(process)d '
        '%(levelname)5s %(module)s:%(lineno)d %(message)s')

    #
    # find and import all packages that might contain spiders
    #
    for get_info in pip.get_installed_distributions():
        match = _egg_name_reg_ex.match(get_info.egg_name())
        if not match:
            continue
        _discover_and_load_all_spiders_in_package(match.group('egg_name'))

    #
    # optionally load all the sample spiders
    #
    if clo.samples:
        _discover_and_load_all_spiders_in_package('cloudfeaster.samples')

    #
    # with all packages loaded that might contain spiders, find all
    # the concrete subclasses of ```cloudfeaster.spider.Spider```
    # which will be the spiders we're interested in
    #
    spiders = _find_concrete_spider_classes(cloudfeaster.spider.Spider)

    print json.dumps(spiders)
