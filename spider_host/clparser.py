"""This module contains all the logic required to parse the
spider host's command line."""

import logging
import optparse

import clparserutil

class CommandLineParser(optparse.OptionParser):

    def __init__(self):
        optparse.OptionParser.__init__(
            self,
            "usage: %prog [options]",
            option_class=clparserutil.Option)

        default = logging.ERROR
        fmt = (
            "logging level "
            "[DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL]"
            " - default = %s"
        )
        help = fmt % logging.getLevelName(default)
        self.add_option(
            "--log",
            action="store",
            dest="logging_level",
            default=default,
            type="logginglevel",
            help=help)

        default = "crawl-request"
        fmt = "crawl request queue name - default = %s"
        help = fmt % default
        self.add_option(
            "--reqq",
            action="store",
            dest="request_queue_name",
            default=default,
            help=help)

        default = "crawl-response"
        fmt = "crawl response queue name - default = %s"
        help = fmt % default
        self.add_option(
            "--resq",
            action="store",
            dest="response_queue_name",
            default=default,
            help=help)

        default = 1
        fmt = "min # seconds to sleep - default = %d"
        help = fmt % default
        self.add_option(
            "--minsleep",
            action="store",
            type="int",
            dest="min_num_secs_to_sleep",
            default=default,
            help=help)

        default = 10
        fmt = "max # seconds to sleep - default = %d"
        help = fmt % default
        self.add_option(
            "--maxsleep",
            action="store",
            type="int",
            dest="max_num_secs_to_sleep",
            default=default,
            help=help)
