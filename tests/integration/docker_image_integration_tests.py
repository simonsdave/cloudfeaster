# -*- coding: utf-8 -*-
"""This module runs integration tests against the Cloudfeaster
docker image which is typically produced as part of the CI process.
"""

import json
import os
import subprocess
import tempfile
import unittest

import jsonschema
from nose.util import safe_str


class IntegrationTestCase(unittest.TestCase):

    def docker_run(self, *docker_run_args):
        stdout_filename = tempfile.mktemp()

        docker_image_name = os.environ.get('CLF_DOCKER_IMAGE', None)
        self.assertIsNotNone(docker_image_name)

        process_args = [
            'docker',
            'run',
            '--rm',
            # After upgrading to Xenial these integration tests
            # started failing with "Chrome failed to start: crashed"
            # after some Googling the problem was traced to Xenial
            # enabling Secure Computing Mode (secomp) for docker
            # containers where Trusty did not have seccomp capability.
            # The referenced issue below is the one that provided the
            # best guidance on how to solve the problem ie. disabling
            # seccomp which is what the next two process args do.
            #
            # https://github.com/SeleniumHQ/docker-selenium/issues/403
            '--security-opt',
            'seccomp:unconfined',
            docker_image_name,
        ]
        process_args.extend(docker_run_args)

        exit_code = subprocess.call(
            process_args,
            stdout=open(stdout_filename, 'w+'),
            stderr=subprocess.STDOUT)

        stdout = []
        with open(stdout_filename, 'r') as fp:
            stdout += [safe_str(fp.read())]

        os.unlink(stdout_filename)

        return (exit_code, stdout)

    def assert_stdout_is_just_json_doc(self, stdout, schema=None, expected_stdout_as_json=None):
        self.assertEqual(1, len(stdout))

        try:
            stdout_as_json = json.loads(stdout[0])
        except Exception as ex:
            self.assertTrue(False, 'stdout is not a json doc - %s' % ex)

        if schema:
            try:
                jsonschema.validate(stdout_as_json, schema)
            except Exception as ex:
                self.assertTrue(False, "stdout output doesn't match jsonschema - %s" % ex)

        if expected_stdout_as_json:
            self.assertEqual(stdout_as_json, expected_stdout_as_json)

        return stdout_as_json


class SpidersDotPyAndDotShIntegrationTestCase(IntegrationTestCase):

    def _test_spiders_dot_something_without_samples(self, cmd):
        expected_stdout_as_json = {}

        (exit_code, stdout) = self.docker_run(cmd)
        self.assertEqual(exit_code, 0)
        self.assert_stdout_is_just_json_doc(
            stdout,
            expected_stdout_as_json=expected_stdout_as_json)

    def test_spiders_dot_py_without_samples(self):
        self._test_spiders_dot_something_without_samples('spiders.py')

    def test_spiders_dot_sh_without_samples(self):
        self._test_spiders_dot_something_without_samples('spiders.sh')

    def _test_spiders_dot_something_with_samples(self, cmd):
        expected_stdout_as_json = {
          "cloudfeaster.samples.pypi.PyPISpider": {
            "url": "https://pypi.python.org/pypi",
            "authenticatingFactors": {
              "password": {
                "pattern": "^.+$"
              }
            },
            "identifyingFactors": {
              "username": {
                "pattern": "^.+$"
              }
            },
            "factorDisplayOrder": [
              "username",
              "password"
            ],
            "factorDisplayNames": {
              "username": {
                "": "username",
                "fr": "nom d'utilisateur",
                "en": "username",
                "ja": u"ユーザー名"
              },
              "password": {
                "": "password",
                "fr": "mot de passe",
                "en": "password",
                "ja": u"パスワード"
              }
            },
            "maxConcurrentCrawls": 3,
            "maxCrawlTimeInSeconds": 30,
            "paranoiaLevel": "low",
            "ttlInSeconds": 60
          },
          "cloudfeaster.samples.pythonwheels_spider.PythonWheelsSpider": {
            "maxConcurrentCrawls": 3,
            "authenticatingFactors": {},
            "url": "https://pythonwheels.com/",
            "factorDisplayOrder": [],
            "maxCrawlTimeInSeconds": 30,
            "identifyingFactors": {},
            "factorDisplayNames": {},
            "paranoiaLevel": "low",
            "ttlInSeconds": 60
          },
          "cloudfeaster.samples.bank_of_canada_daily_exchange_rates.BankOfCanadaDailyExchangeRatesSpider": {
            "maxConcurrentCrawls": 3,
            "authenticatingFactors": {},
            "url": "http://www.bankofcanada.ca/rates/exchange/daily-exchange-rates/",
            "factorDisplayOrder": [],
            "maxCrawlTimeInSeconds": 30,
            "identifyingFactors": {},
            "factorDisplayNames": {},
            "paranoiaLevel": "low",
            "ttlInSeconds": 60
          }
        }

        (exit_code, stdout) = self.docker_run(
            cmd,
            '--samples')
        self.assertEqual(exit_code, 0)
        self.assert_stdout_is_just_json_doc(
            stdout,
            expected_stdout_as_json=expected_stdout_as_json)

    def test_spiders_dot_py_with_samples(self):
        self._test_spiders_dot_something_with_samples('spiders.py')

    def test_spiders_dot_sh_with_samples(self):
        self._test_spiders_dot_something_with_samples('spiders.sh')


class SamplesIntegrationTestCase(IntegrationTestCase):

    def test_spider_host_dot_py_on_boc_fx_rate(self):
        schema = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': 'validate spider output',
            'description': 'validate spider output',
            'type': 'object',
            'properties': {
                'ratesOn': {
                    'type': 'string',
                    # 2018-02-07
                    'pattern': r'^\d{4}\-\d{2}\-\d{2}$',
                },
                'rates': {
                    'patternProperties': {
                        '^.+$': {
                            'type': 'number',
                        },
                    },
                    'additionalProperties': False,
                },
                '_metadata': {
                    'type': 'object',
                    'properties': {
                        'status': {
                            'type': 'object',
                            'properties': {
                                'code': {
                                    'type': 'integer',
                                    'minimum': 0,
                                    'maximum': 0,
                                },
                                'message': {
                                    'type': 'string',
                                    'pattern': 'Ok',
                                },
                            },
                            'required': [
                                'code',
                                'message',
                            ],
                            'additionalProperties': False,
                        },
                        'crawlTime': {
                            'type': 'object',
                            'properties': {
                                'started': {
                                    'type': 'string',
                                    # 2018-02-07T23:52:46.266252+00:00
                                    'pattern': r'^\d{4}\-\d{2}\-\d{2}T\d{2}\:\d{2}\:\d{2}\.\d{6}\+\d{2}\:\d{2}$',
                                },
                                'durationInMs': {
                                    'type': 'integer',
                                    'minimum': 1,
                                },
                            },
                            'required': [
                                'started',
                                'durationInMs',
                            ],
                            'additionalProperties': False,
                        },
                        'spider': {
                            'type': 'object',
                            'properties': {
                                'name': {
                                    'type': 'string',
                                    'pattern': (
                                        'cloudfeaster.samples.bank_of_canada_daily_exchange_rates.'
                                        'BankOfCanadaDailyExchangeRatesSpider'
                                    ),
                                },
                                'version': {
                                    'type': 'string',
                                    # sha1:2a9793fbec2b6bab331ab2994607b03deedd2193
                                    'pattern': r'^sha1:[a-f0-9]{40}$',
                                },
                            },
                            'required': [
                                'version',
                                'name',
                            ],
                            'additionalProperties': False,
                        },
                    },
                    'required': [
                        'status',
                        'crawlTime',
                        'spider',
                    ],
                    'additionalProperties': False,
                },
            },
            'required': [
                'ratesOn',
                'rates',
                '_metadata',
            ],
            'additionalProperties': False,
        }

        (exit_code, stdout) = self.docker_run(
            'spiderhost.py',
            'cloudfeaster.samples.bank_of_canada_daily_exchange_rates.BankOfCanadaDailyExchangeRatesSpider')
        self.assertEqual(exit_code, 0)
        self.assert_stdout_is_just_json_doc(stdout, schema=schema)
