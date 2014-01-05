"""This module contains unit tests for the spider host's queues module."""

import datetime
import json
import shutil
import os
import subprocess
import tempfile
import unittest
import uuid

from keyczar import keyczar
import mock

import clf.spider
from clf.spider_host import queues


class MyMessage(queues.SpiderHostMessage):

    @classmethod
    def get_schema(cls):
        schema = {
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
        return schema


class TestSpiderHostQueue(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # create a directory for the keyczar keyset
        cls._directory_name_for_keyczar_keyset = tempfile.mkdtemp()

        # create keyczar keyset for encryption/decryption
        subprocess_call_args = [
            "keyczart",
            "create",
            ("--location=%s" % cls._directory_name_for_keyczar_keyset),
            "--purpose=crypt",
        ]
        cls._subprocess_call(subprocess_call_args)

        # add a key to the keyczar keyset
        subprocess_call_args = [
            "keyczart",
            "addkey",
            ("--location=%s" % cls._directory_name_for_keyczar_keyset),
            "--status=primary",
        ]
        cls._subprocess_call(subprocess_call_args)

    @classmethod
    def tearDownClass(cls):
        if cls._directory_name_for_keyczar_keyset:
            cls._directory_name_for_keyczar_keyset = None

    @classmethod
    def _subprocess_call(cls, *args):
        with open(os.devnull, "w") as dev_null:
            return subprocess.call(*args, stdout=dev_null, stderr=dev_null)

    def _copy_and_encrypt_spider_args(self, spider_args):
        spider_args = spider_args[:]
        cls = type(self)
        crypter = keyczar.Crypter.Read(cls._directory_name_for_keyczar_keyset)
        for i in range(0, len(spider_args)):
            spider_args[i] = crypter.Encrypt(spider_args[i])
        return spider_args

    def _copy_and_decrypt_spider_args(self, spider_args):
        spider_args = spider_args[:]
        cls = type(self)
        crypter = keyczar.Crypter.Read(cls._directory_name_for_keyczar_keyset)
        for i in range(0, len(spider_args)):
            spider_args[i] = crypter.Decrypt(spider_args[i])
        return spider_args

    def test_write_message_encrypt_all_ok(self):
        """Verify clf.spider_host.queues.SpiderHostQueue.write_message()
        correctly encrypts a message's spider_args before calling
        clf.util.queues.Queue.write_message()."""

        cls = type(self)

        mock_sqs_queue = mock.Mock()
        queue = queues.SpiderHostQueue(mock_sqs_queue)

        unencrypted_spider_args = [
            "dave",
            "was",
            "here",
        ]

        unencrypted_message = MyMessage(
            spider_name="dave",
            spider_args=unencrypted_spider_args[:],
        )

        mock_method_return_value = cls._directory_name_for_keyczar_keyset
        mock_method = mock.Mock(return_value=mock_method_return_value)
        method_name_to_patch = (
            "clf.spider_host.queues."
            "SpiderHostQueue._get_keyczar_keyset_filename"
        )
        with mock.patch(method_name_to_patch, mock_method):
            encrypted_message = queue.write_message(unencrypted_message)
            self.assertIsNotNone(encrypted_message)

            self.assertTrue(encrypted_message is unencrypted_message)

            self.assertEqual(
                len(encrypted_message),
                len(unencrypted_message))

            self.assertEqual(
                encrypted_message.uuid,
                unencrypted_message.uuid)

            self.assertEqual(
                encrypted_message.spider_name,
                unencrypted_message.spider_name)

            self.assertNotEqual(
                encrypted_message.spider_args,
                unencrypted_spider_args)
            self.assertEqual(
                self._copy_and_decrypt_spider_args(encrypted_message.spider_args),
                unencrypted_spider_args)

    def test_write_message_that_is_none(self):
        mock_sqs_queue = mock.Mock()
        queue = queues.SpiderHostQueue(mock_sqs_queue)

        unencrypted_message = None

        mock_write_message_method = mock.Mock(return_value=unencrypted_message)
        name_of_method_to_patch = "clf.util.queues.Queue.write_message"
        with mock.patch(name_of_method_to_patch, mock_write_message_method):
            encrypted_message = queue.write_message(unencrypted_message)
            self.assertIsNone(encrypted_message)

            self.assertEqual(
                mock_write_message_method.call_args_list,
                [mock.call(queue, encrypted_message)])

    def test_read_message_decrypt_all_ok(self):
        mock_sqs_queue = mock.Mock()
        queue = queues.SpiderHostQueue(mock_sqs_queue)

        encrypted_message = MyMessage(
            spider_name="dave",
            spider_args=[
                "dave",
                "was",
                "here",
            ],
        )

        mock_read_message_method = mock.Mock(return_value=encrypted_message)
        name_of_method_to_patch = "clf.util.queues.Queue.read_message"
        with mock.patch(name_of_method_to_patch, mock_read_message_method):
            decrypted_message = queue.read_message()
            self.assertIsNotNone(decrypted_message)

        self.assertEqual(
            mock_read_message_method.call_args_list,
            [mock.call(queue)])

    def test_read_message_no_message_to_decrypt(self):
        mock_sqs_queue = mock.Mock()
        queue = queues.SpiderHostQueue(mock_sqs_queue)

        mock_read_message_method = mock.Mock(return_value=None)
        name_of_method_to_patch = "clf.util.queues.Queue.read_message"
        with mock.patch(name_of_method_to_patch, mock_read_message_method):
            decrypted_message = queue.read_message()
            self.assertIsNone(decrypted_message)

        self.assertEqual(
            mock_read_message_method.call_args_list,
            [mock.call(queue)])


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
        self.assertTrue(4 == len(metrics))
        self._assert_timing_entries_in_metrics_dict(metrics, "crawl")
        self._assert_timing_entries_in_metrics_dict(metrics, "download_spider")
        
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

    def _assert_timing_entries_in_metrics_dict(self, metrics, key_prefix):

        start_time_key = "%s_start_time" % key_prefix
        start_time_as_str = metrics.get(start_time_key, None)
        self.assertIsNotNone(start_time_as_str)
        self.assertTrue(isinstance(start_time_as_str, str))
        start_time = datetime.datetime.strptime(
            start_time_as_str,
            "%a, %d %b %Y %H:%M:%S +0000")
        self.assertIsNotNone(start_time)
        self.assertTrue(isinstance(start_time, datetime.datetime))

        duration_key = "%s_time_in_seconds" % key_prefix
        duration = metrics.get(duration_key, None)
        self.assertIsNotNone(duration)
        self.assertTrue(isinstance(duration, float))
        self.assertTrue(0.0 <= duration)


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
    pass
