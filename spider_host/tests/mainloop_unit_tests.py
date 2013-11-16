"""This module contains unit tests for the spider host's main loop."""

import os
import sys
import unittest

import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import mainloop

class TestMainloop(unittest.TestCase):

    def test_get_messages_returns_empty_collection(self):
        """Verify returning no messages from the request queue
        is handled correctly by mainloop.run()."""

        def get_messages(num_messages):
            mainloop.done = True
            return []
        mock_request_queue = mock.Mock()
        mock_request_queue.get_messages.side_effect = get_messages

        mock_response_queue = mock.Mock()

        mock_rrsleeper = mock.Mock()
        rv = mainloop.run(
            mock_request_queue,
            mock_response_queue,
            mock_rrsleeper)
        self.assertIsNotNone(rv)
        self.assertEqual(rv, mainloop.rv_ok)
        self.assertEqual(
            mock_rrsleeper.sleep.call_args_list,
            [mock.call()])

        self.assertEqual(
            mock_request_queue.get_messages.call_args_list,
            [mock.call(1)])
