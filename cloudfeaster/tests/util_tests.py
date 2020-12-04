"""This module contains unit tests for the ```privacy``` module."""

import os
import unittest
import uuid

from .. import util


class TestFileToDataUriScheme(unittest.TestCase):

    def test_none_filename(self):
        self.assertIsNone(util.file_to_data_uri_scheme(None))

    def test_empty_filename(self):
        self.assertIsNone(util.file_to_data_uri_scheme(''))

    def test_filename_does_not_exist(self):
        self.assertIsNone(util.file_to_data_uri_scheme(uuid.uuid4().hex))

    def test_zero_byte_file(self):
        filename = os.path.join(
            os.path.dirname(__file__),
            'data',
            'empty.txt')
        self.assertIsNone(util.file_to_data_uri_scheme(filename))

    def test_png(self):
        filename = os.path.join(
            os.path.dirname(__file__),
            'data',
            'screenshot.png')
        self.assertTrue(util.file_to_data_uri_scheme(filename).startswith('data:image/png;base64,'))

    def test_pdf(self):
        filename = os.path.join(
            os.path.dirname(__file__),
            'data',
            'python-magic-pypi.pdf')
        self.assertTrue(util.file_to_data_uri_scheme(filename).startswith('data:application/pdf;base64,'))

    def test_json(self):
        filename = os.path.join(
            os.path.dirname(__file__),
            'data',
            'crawl-output.json')
        self.assertTrue(util.file_to_data_uri_scheme(filename).startswith('data:application/json;base64,'))

    def test_txt(self):
        filename = os.path.join(
            os.path.dirname(__file__),
            'data',
            'chrome-driver-log.txt')
        self.assertTrue(util.file_to_data_uri_scheme(filename).startswith('data:text/plain;base64,'))
