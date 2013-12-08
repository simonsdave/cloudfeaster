"""This module contains unit tests for the spider host's mainloop module."""

import unittest

import mock

from clf.spider_host.queues import CrawlResponseMessage
from clf.spider_host import mainloop


class TestMainloop(unittest.TestCase):

    def setUp(self):
        mainloop.done = False

    def test_run_on_read_message_returns_none(self):
        """Verify returning no messages from the request queue
        is handled correctly by mainloop.run()."""

        def read_message():
            mainloop.done = True
            return None
        mock_request_queue = mock.Mock()
        mock_request_queue.read_message.side_effect = read_message

        mock_response_queue = mock.Mock()

        mock_rrsleeper = mock.Mock()

        mock_local_spider_repo = mock.Mock()

        mainloop.run(
            mock_request_queue,
            mock_response_queue,
            mock_rrsleeper,
            mock_local_spider_repo)

        self.assertEqual(
            mock_request_queue.read_message.call_args_list,
            [mock.call()])

        print mock_rrsleeper.sleep.call_args_list
        self.assertEqual(
            mock_rrsleeper.sleep.call_args_list,
            [mock.call()])

    def test_run_on_read_message_returns_non_none(self):
        """Verify returning a message from the request queue
        is handled correctly by mainloop.run()."""

        mock_request_queue = mock.Mock()

        mock_crawl_responses = []

        def create_mock_message():
            mock_message = mock.Mock()
            mock_crawl_response = mock.Mock()
            mock_message.process.return_value = mock_crawl_response
            mock_crawl_responses.append(mock_crawl_response)
            return mock_message
        mock_messages = [create_mock_message() for i in range(0, 9)]
        end_mainloop_message = mock.Mock()

        def end_mainloop(spider_repo):
            mainloop.done = True
            mock_crawl_response = mock.Mock()
            mock_crawl_responses.append(mock_crawl_response)
            return mock_crawl_response
        end_mainloop_message.process.side_effect = end_mainloop
        mock_messages.append(end_mainloop_message)

        mock_request_queue.read_message.side_effect = mock_messages

        def write_message(message):
            self.assertIsNotNone(message)
            self.assertEqual(CrawlResponseMessage, type(message))
        mock_response_queue = mock.Mock()
        mock_response_queue.write_message.side_effect = write_message

        mock_rrsleeper = mock.Mock()

        mock_local_spider_repo = mock.Mock()

        mainloop.run(
            mock_request_queue,
            mock_response_queue,
            mock_rrsleeper,
            mock_local_spider_repo)

        # read_message always returned something should never have slept
        self.assertEqual(mock_rrsleeper.sleep.call_args_list, [])

        # should have called request queue's read_message()
        # once for each of the messages in mock_messages
        self.assertEqual(
            mock_request_queue.read_message.call_args_list,
            [mock.call() for i in range(0, len(mock_messages))])

        # each mock message should have its process() and delete()
        # methods called once with no arguments
        for mock_message in mock_messages:
            self.assertEqual(
                mock_message.process.call_args_list,
                [mock.call(mock_local_spider_repo)])
            self.assertEqual(
                mock_message.delete.call_args_list,
                [mock.call()])

        # should have called request queue's write_message()
        # once for each of the messages in mock_messages
        self.assertEqual(
            len(mock_response_queue.write_message.mock_calls),
            len(mock_crawl_responses))
