"""This module contains unit tests for the ```privacy``` module."""

import re
import unittest

from .. import privacy


class TestHashSpiderArg(unittest.TestCase):

    def test_ok_no_data(self):
        spider_arg = 'something sensitive'
        hashed_spider_arg = privacy.hash_spider_arg(spider_arg)
        self.assertNotEqual(spider_arg, hashed_spider_arg)
        reg_ex = re.compile(r'^[^\s]+:[^\s]+$')
        self.assertTrue(reg_ex.match(hashed_spider_arg))
