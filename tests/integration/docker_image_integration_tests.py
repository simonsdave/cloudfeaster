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


class SpidersDotPyIntegrationTestCase(IntegrationTestCase):

    def test_spiders_dot_py_without_samples(self):
        expected_stdout_as_json = {}

        (exit_code, stdout) = self.docker_run('spiders.py')
        self.assertEqual(exit_code, 0)
        self.assert_stdout_is_just_json_doc(stdout, expected_stdout_as_json=expected_stdout_as_json)

    def test_spiders_dot_py_with_samples(self):
        expected_stdout_as_json = {
            'cloudfeaster.samples.pypi_spider.PyPISpider': {
                'url': 'http://pypi-ranking.info/alltime',
                'factor_display_order': [],
                'max_crawl_time_in_seconds': 30,
                'max_concurrency': 3,
                'ttl_in_seconds': 60,
                'factor_display_names': {},
                'paranoia_level': 'low',
            },
            'cloudfeaster.samples.bank_of_canada_daily_exchange_rates.BankOfCanadaDailyExchangeRatesSpider': {
                'url': 'http://www.bankofcanada.ca/rates/exchange/daily-exchange-rates/',
                'factor_display_order': [],
                'max_crawl_time_in_seconds': 30,
                'max_concurrency': 3,
                'ttl_in_seconds': 60,
                'factor_display_names': {},
                'paranoia_level': 'low',
            }
        }

        (exit_code, stdout) = self.docker_run(
            'spiders.py',
            '--samples')
        self.assertEqual(exit_code, 0)
        self.assert_stdout_is_just_json_doc(stdout, expected_stdout_as_json=expected_stdout_as_json)


class SamplesIntegrationTestCase(IntegrationTestCase):

    def test_spider_host_dot_py_on_boc_fx_rate(self):
        schema = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': 'validate spider output',
            'description': 'validate spider output',
            'type': 'object',
            'properties': {
                'rates_on': {
                    'type': 'string',
                    # 2018-02-07
                    'pattern': '^\d{4}\-\d{2}\-\d{2}$',
                },
                'rates': {
                    'patternProperties': {
                        '^.+$': {
                            'type': 'number',
                        },
                    },
                    'additionalProperties': False,
                },
                '_status': {
                    'type': 'string',
                    'pattern': 'Ok',
                },
                '_status_code': {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 0,
                },
                '_crawl_time': {
                    'type': 'string',
                    # 2018-02-07T23:52:46.266252+00:00
                    'pattern': '^\d{4}\-\d{2}\-\d{2}T\d{2}\:\d{2}\:\d{2}\.\d{6}\+\d{2}\:\d{2}$',
                },
                '_crawl_time_in_ms': {
                    'type': 'integer',
                    'minimum': 1,
                },
                '_spider': {
                    'type': 'object',
                    'properties': {
                        'version': {
                            'type': 'string',
                            # sha1:2a9793fbec2b6bab331ab2994607b03deedd2193
                            'pattern': '^sha1:[a-f0-9]{40}$',
                        },
                        'name': {
                            'type': 'string',
                            'pattern': (
                                'cloudfeaster.samples.bank_of_canada_daily_exchange_rates.'
                                'BankOfCanadaDailyExchangeRatesSpider'
                            ),
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
                'rates_on',
                '_status',
                '_status_code',
                '_crawl_time',
                '_crawl_time_in_ms',
            ],
            'additionalProperties': False,
        }

        (exit_code, stdout) = self.docker_run(
            'spiderhost.py',
            'cloudfeaster.samples.bank_of_canada_daily_exchange_rates.BankOfCanadaDailyExchangeRatesSpider')
        self.assertEqual(exit_code, 0)
        self.assert_stdout_is_just_json_doc(stdout, schema=schema)