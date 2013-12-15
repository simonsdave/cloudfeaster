"""This module contains unit tests for the spider host's queues module."""

import unittest

import mock

import clf.spider
from clf.spider_host import queues


class TestCrawlRequestQueue(unittest.TestCase):

    def test_get_message_class_returns_expected_message_class(self):
        self.assertEqual(
            queues.CrawlRequestQueue.get_message_class(),
            queues.CrawlRequestMessage)

    def test_get_queue_name_prefix_returns_expected_prefix(self):
        self.assertEqual(
            queues.CrawlRequestQueue.get_queue_name_prefix(),
            "clf_creq_")


class TestCrawlRequestMessage(unittest.TestCase):

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
            queues.CrawlRequestMessage.get_schema(),
            expected_schema)

    def test_process_spider_not_found(self):
        """Verify that when a spider can't be found we get
        a ```clf.spider.SC_SPIDER_NOT_FOUND``` response
        from ```queues.CrawlRequestMessage.process()```."""
        message = queues.CrawlRequestMessage(
            spider_name="dave",
            spider_args=[])
        local_spider_repo = mock.Mock()
        local_spider_repo.get_spider_class.return_value = None
        cr = message.process(local_spider_repo)
        self.assertIsNotNone(cr)
        self.assertEqual(cr.status_code, clf.spider.SC_SPIDER_NOT_FOUND)        
        self.assertEqual(
            local_spider_repo.get_spider_class.call_args_list,
            [mock.call(message.spider_name)])

    def test_process_all_good(self):
        """Verify the 'all good' scenario when calling
        ```queues.CrawlRequestMessage.process()```."""
        message = queues.CrawlRequestMessage(
            spider_name="dave",
            spider_args=[1, 2, 3])

        spider_walk_return_value_mock = mock.Mock()
        spider_mock = mock.Mock()
        spider_mock.walk.return_value = spider_walk_return_value_mock

        spider_class_mock = mock.Mock(return_value=spider_mock)

        local_spider_repo = mock.Mock()
        local_spider_repo.get_spider_class.return_value = spider_class_mock

        cr = message.process(local_spider_repo)

        self.assertIsNotNone(cr)
        self.assertEqual(cr, spider_walk_return_value_mock)

        self.assertEqual(
            local_spider_repo.get_spider_class.call_args_list,
            [mock.call(message.spider_name)])

        self.assertEqual(
            spider_mock.walk.call_args_list,
            [mock.call(*message.spider_args)])

        self.assertEqual(
            spider_class_mock.call_args_list,
            [mock.call()])


class TestCrawlResponseQueue(unittest.TestCase):

    def test_get_message_class_returns_expected_message_class(self):
        self.assertEqual(
            queues.CrawlResponseQueue.get_message_class(),
            queues.CrawlResponseMessage)

    def test_get_queue_name_prefix_returns_expected_prefix(self):
        self.assertEqual(
            queues.CrawlResponseQueue.get_queue_name_prefix(),
            "clf_cres_")


class TestCrawlResponseMessage(unittest.TestCase):

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
            },
            "required": [
                "uuid",
                "spider_name",
                "spider_args",
                "crawl_response",
            ],
            "additionalProperties": False,
        }
        self.assertEqual(
            queues.CrawlResponseMessage.get_schema(),
            expected_schema)
