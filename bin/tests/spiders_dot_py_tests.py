# -*- coding: utf-8 -*-
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
            stdout=subprocess.PIPE)
        (stdout, _) = p.communicate()
        self.assertEqual(p.returncode, 0)
        self.assertEqual(stdout, '{}\n')

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
            stdout=subprocess.PIPE)
        (stdout, _) = p.communicate()
        self.assertEqual(p.returncode, 0)
        expected_stdout = {
          "cloudfeaster.samples.pypi.PyPISpider": {
            "url": "https://pypi.python.org/pypi",
            "identifyingFactors": {
              "username": {
                "pattern": "^.+$",
              },
            },
            "authenticatingFactors": {
              "password": {
                "pattern": "^.+$",
              },
            },
            "factorDisplayOrder": [
              "username",
              "password",
            ],
            "factorDisplayNames": {
              "username": {
                "": "username",
                "fr": "nom d'utilisateur",
                "en": "username",
                "ja": u"ユーザー名",
              },
              "password": {
                "": "password",
                "fr": "mot de passe",
                "en": "password",
                "ja": u"パスワード",
              }
            },
            "maxConcurrentCrawls": 3,
            "maxCrawlTimeInSeconds": 30,
            "paranoiaLevel": "low",
            "ttlInSeconds": 60,
          },
          "cloudfeaster.samples.pythonwheels_spider.PythonWheelsSpider": {
            "url": "https://pythonwheels.com/",
            "identifyingFactors": {},
            "authenticatingFactors": {},
            "factorDisplayOrder": [],
            "factorDisplayNames": {},
            "ttlInSeconds": 60,
            "paranoiaLevel": "low",
            "maxConcurrentCrawls": 3,
            "maxCrawlTimeInSeconds": 30,
          },
          "cloudfeaster.samples.bank_of_canada_daily_exchange_rates.BankOfCanadaDailyExchangeRatesSpider": {
            "url": "http://www.bankofcanada.ca/rates/exchange/daily-exchange-rates/",
            "identifyingFactors": {},
            "authenticatingFactors": {},
            "factorDisplayOrder": [],
            "factorDisplayNames": {},
            "ttlInSeconds": 60,
            "paranoiaLevel": "low",
            "maxConcurrentCrawls": 3,
            "maxCrawlTimeInSeconds": 30,
          }
        }
        self.assertEqual(json.loads(stdout), expected_stdout)
