"""This module contains unit tests for the ```privacy``` module."""

import re
import unittest

from .. import privacy


class TestHashSpiderArg(unittest.TestCase):

    def test_ok_no_data(self):
        crawl_arg = 'something sensitive'
        hashed_crawl_arg = privacy.hash_crawl_arg(crawl_arg)
        self.assertNotEqual(crawl_arg, hashed_crawl_arg)
        reg_ex = re.compile(r'^[^\s]+:[^\s]+$')
        self.assertTrue(reg_ex.match(hashed_crawl_arg))
