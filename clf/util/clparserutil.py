"""This module contains a series of generally useful and reusable
components for use when building extensions to the optparse module
which parses command lines."""

import re
import logging
import optparse

_logger = logging.getLogger("UTIL.%s" % __name__)


def _check_couchdb(option, opt, value):
    """Type checking function for command line parser's 'couchdb' type."""
    reg_ex_pattern = "^[^\s]+\:\d+\/[^\s]+$"
    reg_ex = re.compile(reg_ex_pattern)
    if reg_ex.match(value):
        return value
    msg = "option %s: required format is host:port/database" % opt
    raise optparse.OptionValueError(msg)


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
    'hostcolonport' type."""
    reg_ex_pattern = "^[^\s]+\:\d+$"
    reg_ex = re.compile(reg_ex_pattern)
    if reg_ex.match(value):
        return value
    msg = "option %s: should be host:port format" % opt
    raise optparse.OptionValueError(msg)


def _check_memcached(option, opt, value):
    """Type checking function for command line parser's
    'memcached' type."""
    split_reg_ex = re.compile("\s*\,\s*")
    host_colon_port_reg_ex = re.compile("^[^\:]+\:\d+$")
    rv = []
    for server in split_reg_ex.split(value.strip()):
        if not host_colon_port_reg_ex.match(server):
            fmt = (
                "option %s: should be 'host:port, host:port, ... "
                "host:port' format"
            )
            raise optparse.OptionValueError(fmt % opt)
        rv.append(server)
    return rv


def _check_boolean(option, opt, value):
    """Type checking function for command line parser's 'boolean' type."""
    true_reg_ex_pattern = "^(true|t|y|yes|1)$"
    true_reg_ex = re.compile(true_reg_ex_pattern, re.IGNORECASE)
    if true_reg_ex.match(value):
        return True
    false_reg_ex_pattern = "^(false|f|n|no|0)$"
    false_reg_ex = re.compile(false_reg_ex_pattern, re.IGNORECASE)
    if false_reg_ex.match(value):
        return False
    msg = "option %s: should be one of true, false, yes, no, 1 or 0" % opt
    raise optparse.OptionValueError(msg)


class Option(optparse.Option):
    """Adds couchdb, hostcolonport, boolean & logginglevel types to the
    command line parser's list of available types."""
    new_types = (
        "hostcolonport",
        "logginglevel",
        "boolean",
        "couchdb",
        "memcached",
    )
    TYPES = optparse.Option.TYPES + new_types
    TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
    TYPE_CHECKER["hostcolonport"] = _check_host_colon_port
    TYPE_CHECKER["logginglevel"] = _check_logging_level
    TYPE_CHECKER["boolean"] = _check_boolean
    TYPE_CHECKER["couchdb"] = _check_couchdb
    TYPE_CHECKER["memcached"] = _check_memcached
