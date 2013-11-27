"""This module contains unit tests for rrsleeper's RRSleeper."""

import os
import sys
import unittest

import mock

from clf.util.rrsleeper import RRSleeper

class TestRandomRangeSleeper(unittest.TestCase):

    def test_sleep_interval_within_acceptable_range(self):
        min_num_secs_to_sleep = 1
        max_num_secs_to_sleep = 15
        sleeper = RRSleeper(min_num_secs_to_sleep, max_num_secs_to_sleep)
        for i in range(1, 1000):
            self.my_num_secs_slept = None
            def time_sleep_patch(seconds):
                self.assertIsNone(self.my_num_secs_slept)
                self.my_num_secs_slept = seconds
            with mock.patch("time.sleep", time_sleep_patch):
                num_secs_slept = sleeper.sleep()
                self.assertIsNotNone(self.my_num_secs_slept)
                self.assertEqual(self.my_num_secs_slept, num_secs_slept)
                self.assertTrue(min_num_secs_to_sleep <= num_secs_slept)
                self.assertTrue(num_secs_slept <= max_num_secs_to_sleep)
