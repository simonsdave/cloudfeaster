"""This module contains unit tests for the spider host's command
line parser."""

import logging
import unittest

from clf.spider_host.clparser import CommandLineParser


class TestCommandLineParser(unittest.TestCase):

    def test_defaults(self):
        """Verify the command line parser's default values."""
        clp = CommandLineParser()
        (clo, cla) = clp.parse_args([])
        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.crawl_request_queue_name, "crawl_request")
        self.assertEqual(clo.crawl_response_queue_name, "crawl_response")
        self.assertEqual(clo.min_num_secs_to_sleep, 0)
        self.assertEqual(clo.max_num_secs_to_sleep, 5)
