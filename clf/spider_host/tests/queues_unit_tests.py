"""This module contains unit tests for the spider host's queues module."""

import datetime
import json
import unittest

import mock

import clf.spider
from clf.spider_host import queues


class TestCrawlRequestQueue(unittest.TestCase):

    def test_get_message_class_returns_expected_message_class(self):
        self.assertEqual(
            queues.CrawlRequestQueue.get_message_class(),
            queues.CrawlRequest)

    def test_get_queue_name_prefix_returns_expected_prefix(self):
        self.assertEqual(
            queues.CrawlRequestQueue.get_queue_name_prefix(),
            "clf_creq_")


class TestCrawlRequest(unittest.TestCase):

    def test_get_schema_returns_expected_schema(self):
        expected_schema = {
            "type": "object",
            "properties": {
                "uuid": {
                    "type": "string",
                    "minLength": 1,
                },
                "spider_name": {
                    "type": "string",
                    "minLength": 1,
                },
                "spider_args": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 1,
                    },
                },
            },
            "required": [
                "uuid",
                "spider_name",
                "spider_args",
            ],
            "additionalProperties": False,
        }
        self.assertEqual(
            queues.CrawlRequest.get_schema(),
            expected_schema)

    def test_process_spider_not_found(self):
        """Verify that when a spider can't be found we get
        a ```clf.spider.SC_SPIDER_NOT_FOUND``` response
        from ```queues.CrawlRequest.process()```."""
        message = queues.CrawlRequest(
            spider_name="dave",
            spider_args=[])
        local_spider_repo = mock.Mock()
        local_spider_repo.get_spider_class.return_value = None
        crawl_response = message.process(local_spider_repo)
        self.assertIsNotNone(crawl_response)
        cr = crawl_response.crawl_response
        self.assertIsNotNone(cr)
        self.assertEqual(cr.status_code, clf.spider.SC_SPIDER_NOT_FOUND)        
        self.assertEqual(
            local_spider_repo.get_spider_class.call_args_list,
            [mock.call(message.spider_name)])

    def test_process_all_good(self):
        """Verify the 'all good' scenario when calling
        ```queues.CrawlRequest.process()```."""
        crawl_request = queues.CrawlRequest(
            spider_name="dave",
            spider_args=[1, 2, 3])

        spider_walk_return_value_mock = mock.Mock()
        spider_mock = mock.Mock()
        spider_mock.walk.return_value = spider_walk_return_value_mock

        spider_class_mock = mock.Mock(return_value=spider_mock)

        local_spider_repo = mock.Mock()
        local_spider_repo.get_spider_class.return_value = spider_class_mock

        crawl_response = crawl_request.process(local_spider_repo)

        self.assertIsNotNone(crawl_response)

        # crawl response should have same basic parameters as
        # as crawl request
        self.assertEqual(crawl_request.uuid, crawl_response.uuid)
        self.assertEqual(crawl_request.spider_name, crawl_response.spider_name)
        self.assertEqual(crawl_request.spider_args, crawl_response.spider_args)

        # crawl response should have a metrics attribute that's
        # a dict with 2 entries (crawl_start_time and crawl_time_in_seconds).
        metrics = crawl_response.metrics
        self.assertIsNotNone(metrics)

        self.assertTrue(isinstance(metrics, dict))
        self.assertTrue(2 == len(metrics))

        crawl_start_time_as_str = metrics.get("crawl_start_time", None)
        self.assertIsNotNone(crawl_start_time_as_str)
        self.assertTrue(isinstance(crawl_start_time_as_str, str))
        crawl_start_time = datetime.datetime.strptime(
            crawl_start_time_as_str,
            "%a, %d %b %Y %H:%M:%S +0000")
        self.assertIsNotNone(crawl_start_time)
        self.assertTrue(isinstance(crawl_start_time, datetime.datetime))

        crawl_time_in_seconds = metrics.get("crawl_time_in_seconds", None)
        self.assertIsNotNone(crawl_time_in_seconds)
        self.assertTrue(isinstance(crawl_time_in_seconds, float))
        self.assertTrue(0.0 <= crawl_time_in_seconds)
        
        # ...

        cr = crawl_response.crawl_response
        self.assertIsNotNone(cr)
        self.assertEqual(cr, spider_walk_return_value_mock)

        self.assertEqual(
            local_spider_repo.get_spider_class.call_args_list,
            [mock.call(crawl_request.spider_name)])

        self.assertEqual(
            spider_mock.walk.call_args_list,
            [mock.call(*crawl_request.spider_args)])

        self.assertEqual(
            spider_class_mock.call_args_list,
            [mock.call()])


class TestCrawlResponseQueue(unittest.TestCase):

    def test_get_message_class_returns_expected_message_class(self):
        self.assertEqual(
            queues.CrawlResponseQueue.get_message_class(),
            queues.CrawlResponse)

    def test_get_queue_name_prefix_returns_expected_prefix(self):
        self.assertEqual(
            queues.CrawlResponseQueue.get_queue_name_prefix(),
            "clf_cres_")


class TestCrawlResponse(unittest.TestCase):

    def test_get_schema_returns_expected_schema(self):
        expected_schema = {
            "type": "object",
            "properties": {
                "uuid": {
                    "type": "string",
                    "minLength": 1,
                },
                "spider_name": {
                    "type": "string",
                    "minLength": 1,
                },
                "spider_args": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 1,
                    },
                },
                "crawl_response": {
                    "type": "object",
                },
                "metrics": {
                    "type": "object",
                },
            },
            "required": [
                "uuid",
                "spider_name",
                "spider_args",
                "crawl_response",
                "metrics",
            ],
            "additionalProperties": False,
        }
        self.assertEqual(
            queues.CrawlResponse.get_schema(),
            expected_schema)
