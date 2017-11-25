"""This module contains "unit" tests for ```spiders.py```."""

import json
import subprocess
import unittest

from nose.plugins.attrib import attr


@attr('integration')
class TestSpidersDotPy(unittest.TestCase):

    def test_all_good(self):
        p = subprocess.Popen(
            ['spiders.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        (stdout_and_stderr, _) = p.communicate()
        self.assertEqual(p.returncode, 0)
        self.assertEqual(stdout_and_stderr, '{}\n')

    def test_invalid_command_line_args(self):
        p = subprocess.Popen(
            ['spiders.py', 'dave-creates-an-error'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        (stdout_and_stderr, _) = p.communicate()
        self.assertEqual(p.returncode, 2)
        self.assertEqual(
            stdout_and_stderr,
            'Usage: spiders.py [options] <package>\n\nspiders.py: error: try again ...\n')

    def test_load_sample_spiders(self):
        p = subprocess.Popen(
            ['spiders.py', '--samples'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        (stdout_and_stderr, _) = p.communicate()
        self.assertEqual(p.returncode, 0)
        expected_stdout_and_stderr = {
          "cloudfeaster.samples.pypi_spider.PyPISpider": {
            "url": "http://pypi-ranking.info/alltime",
            "factor_display_names": {},
            "ttl": 60,
            "factor_display_order": []
          },
          "cloudfeaster.samples.bank_of_canada_daily_exchange_rates.BankOfCanadaDailyExchangeRatesSpider": {
            "url": "http://www.bankofcanada.ca/rates/exchange/daily-exchange-rates/",
            "factor_display_names": {},
            "ttl": 60,
            "factor_display_order": []
          }
        }
        self.assertEqual(json.loads(stdout_and_stderr), expected_stdout_and_stderr)
