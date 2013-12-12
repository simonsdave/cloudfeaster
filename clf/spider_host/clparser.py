"""This module contains all the logic required to parse the
spider host's command line."""

import logging
import optparse

from clf.util import clparserutil


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

        default = "crawl_request"
        fmt = "crawl request queue name - default = %s"
        help = fmt % default
        self.add_option(
            "--reqq",
            action="store",
            dest="crawl_request_queue_name",
            default=default,
            help=help)

        default = "crawl_response"
        fmt = "crawl response queue name - default = %s"
        help = fmt % default
        self.add_option(
            "--resq",
            action="store",
            dest="crawl_response_queue_name",
            default=default,
            help=help)

        default = "spider_repo"
        fmt = "spider repo name - default = %s"
        help = fmt % default
        self.add_option(
            "--sr",
            action="store",
            dest="spider_repo_name",
            default=default,
            help=help)

        default = 0
        fmt = "min # seconds to sleep - default = %d"
        help = fmt % default
        self.add_option(
            "--minsleep",
            action="store",
            type="int",
            dest="min_num_secs_to_sleep",
            default=default,
            help=help)

        default = 5
        fmt = "max # seconds to sleep - default = %d"
        help = fmt % default
        self.add_option(
            "--maxsleep",
            action="store",
            type="int",
            dest="max_num_secs_to_sleep",
            default=default,
            help=help)
