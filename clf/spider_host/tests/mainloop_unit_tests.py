"""This module contains unit tests for the spider host's main loop."""

import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import mainloop

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

        mainloop.run(
            mock_request_queue,
            mock_response_queue,
            mock_rrsleeper)

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

        mock_messages = [mock.Mock() for i in range(0, 9)]
        end_mainloop_message = mock.Mock()
        def end_mainloop():
            mainloop.done = True
        end_mainloop_message.process.side_effect = end_mainloop
        mock_messages.append(end_mainloop_message)

        mock_request_queue.read_message.side_effect = mock_messages

        mock_response_queue = mock.Mock()

        mock_rrsleeper = mock.Mock()

        mainloop.run(
            mock_request_queue,
            mock_response_queue,
            mock_rrsleeper)

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
                [mock.call()])
            self.assertEqual(
                mock_message.delete.call_args_list,
                [mock.call()])
