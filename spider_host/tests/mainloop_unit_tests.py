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

    def _generate_unique_nonzero_length_str(self):
        return str(uuid.uuid4()).replace('-','')        

#        def get_queue_patch(sqs_conn, queue_name):
#            self.assertIsNotNone(queue_name)
#            return None
