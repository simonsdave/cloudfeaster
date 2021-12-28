#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import hashlib
import inspect
import json
import logging
import optparse
import os
import re
import sys
import time

import cloudfeaster
from cloudfeaster.spider import SpiderDiscovery
import cloudfeaster.samples


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
            'usage: %prog [options]',
            description='discover spiders',
            version='%%prog %s' % cloudfeaster.__version__,
            option_class=CommandLineOption)

        default = False
        fmt = 'include sample spiders - default = {default}'
        help = fmt.format(default=default)
        self.add_option(
            '--samples',
            action='store_true',
            dest='samples',
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
        if len(cla) != 0:
            sys.stderr.write(self.get_usage())
            sys.exit(0)

        return (clo, cla)


if __name__ == "__main__":
    #
    # parse command line
    #
    clp = CommandLineParser()
    (clo, cla) = clp.parse_args()

    #
    # configure logging ... remember gmt = utc
    #
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        level=clo.logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s')

    #
    # now discover some spiders:-)
    #
    sd = SpiderDiscovery(clo.samples)
    output = sd.discover()

    #
    # add _metadata
    #
    module = sys.modules['__main__']
    source = inspect.getsource(module)
    version_hash = hashlib.sha256(source.encode('UTF-8'))

    output['_metadata'] = {
        'name': os.path.basename(__file__),
        'version': '{name}:{hash_digest}'.format(name=version_hash.name, hash_digest=version_hash.hexdigest()),
    }

    #
    # finally generate some stdout
    #
    print(json.dumps(output))

    sys.exit(0)
