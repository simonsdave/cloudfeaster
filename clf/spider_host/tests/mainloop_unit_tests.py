"""This module contains unit tests for the spider host's main loop."""

import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import mainloop

class TestMainloop(unittest.TestCase):

    def test_read_message_return_none(self):
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
            mock_rrsleeper.sleep.call_args_list,
            [mock.call()])

        self.assertEqual(
            mock_request_queue.read_message.call_args_list,
            [mock.call()])
