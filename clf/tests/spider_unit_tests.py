"""This module contains unit tests for the ```spider``` module."""

import os
import sys
import unittest
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import spider

class TestCrawlResponse(unittest.TestCase):

	def test_ctr_with_just_status_code_ok(self):
		status_code = 42
		cr = spider.CrawlResponse(status_code)
		self.assertEqual(cr.status_code, status_code)
		self.assertIsNone(cr.data)
		self.assertIsNone(cr.status)

	def test_ctr_with_status_code_and_status_ok(self):
		status_code = 42
		status = str(uuid.uuid4())
		cr = spider.CrawlResponse(status_code, status=status)
		self.assertEqual(cr.status_code, status_code)
		self.assertIsNone(cr.data)
		self.assertEqual(cr.status, status)

	def test_ctr_with_status_code_status_and_data_ok(self):
		status_code = 42
		status = str(uuid.uuid4())
		data = {
            'data1': str(uuid.uuid4()),
            'data2': str(uuid.uuid4()),
        }
		cr = spider.CrawlResponse(status_code, data, status)
		self.assertEqual(cr.status_code, status_code)
		self.assertEqual(cr.data, data)
		self.assertEqual(cr.status, status)
