"""This module contains unit tests for the spider host's main loop."""

import os
import sys
import unittest
import uuid

import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import mainloop

class TestMainloop(unittest.TestCase):

    def test_request_queue_not_found(self):
        """Verify when mainloop.run() is called with a request queue
        name that does not exist the main loop ends immediately with
        the expected error code."""
        request_queue_name = self._generate_unique_nonzero_length_str()
        response_queue_name = self._generate_unique_nonzero_length_str()
        min_num_secs_to_sleep = 1
        max_num_secs_to_sleep = 15

        get_queue_patch = mock.Mock(return_value=None)

        method_name_to_patch = "boto.sqs.connection.SQSConnection.get_queue"
        with mock.patch(method_name_to_patch, get_queue_patch):
            rv = mainloop.run(
                request_queue_name,
                response_queue_name,
                min_num_secs_to_sleep,
                max_num_secs_to_sleep)
            self.assertIsNotNone(rv)
            self.assertEqual(rv, mainloop.rv_request_queue_not_found)

        get_queue_patch.assert_called_once_with(request_queue_name)

    def test_response_queue_not_found(self):
        """Verify when mainloop.run() is called with a response queue
        name that does not exist the main loop ends immediately with
        the expected error code."""
        request_queue_name = self._generate_unique_nonzero_length_str()
        response_queue_name = self._generate_unique_nonzero_length_str()
        min_num_secs_to_sleep = 1
        max_num_secs_to_sleep = 15

        get_queue_patch = mock.Mock()
        def get_queue(queue_name):
            return mock.Mock() if queue_name == request_queue_name else None
        get_queue_patch.side_effect = get_queue

        method_name_to_patch = "boto.sqs.connection.SQSConnection.get_queue"
        with mock.patch(method_name_to_patch, get_queue_patch):
            rv = mainloop.run(
                request_queue_name,
                response_queue_name,
                min_num_secs_to_sleep,
                max_num_secs_to_sleep)
            self.assertIsNotNone(rv)
            self.assertEqual(rv, mainloop.rv_response_queue_not_found)

        expected_calls = [
            mock.call(request_queue_name),
            mock.call(response_queue_name)
        ]
        self.assertEqual(get_queue_patch.call_args_list, expected_calls)

    def test_rrsleeper_args_passed_correctly(self):
        """Verify the min and max secs to sleep args pass to mainloop.run()
        are correctly passed to rrsleeper."""
        request_queue_name = self._generate_unique_nonzero_length_str()
        response_queue_name = self._generate_unique_nonzero_length_str()
        min_num_secs_to_sleep = 1
        max_num_secs_to_sleep = 15

        get_queue_patch = mock.Mock(return_value=mock.Mock())
        method_name_to_patch = "boto.sqs.connection.SQSConnection.get_queue"
        with mock.patch(method_name_to_patch, get_queue_patch):

            rrsleeper_patch = mock.Mock(return_value=mock.Mock())
            with mock.patch("rrsleeper.RRSleeper", rrsleeper_patch):
                mainloop.done = True
                rv = mainloop.run(
                    request_queue_name,
                    response_queue_name,
                    min_num_secs_to_sleep,
                    max_num_secs_to_sleep)
                self.assertIsNotNone(rv)
                self.assertEqual(rv, mainloop.rv_ok)

            rrsleeper_patch.assert_called_once_with(
                min_num_secs_to_sleep,
                max_num_secs_to_sleep)

    def _generate_unique_nonzero_length_str(self):
        return str(uuid.uuid4()).replace('-','')        
