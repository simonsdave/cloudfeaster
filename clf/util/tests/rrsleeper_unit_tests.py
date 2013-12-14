"""This module contains unit tests for clf.util.rrsleeper.RRSleeper"""

import os
import sys
import unittest

import mock

from clf.util.rrsleeper import RRSleeper

class TestRandomRangeSleeper(unittest.TestCase):

    def test_ctr(self):
        min_num_secs_to_sleep = 1
        max_num_secs_to_sleep = 15
        self.assertTrue(min_num_secs_to_sleep < max_num_secs_to_sleep)
        sleeper = RRSleeper(
            min_num_secs_to_sleep,
            max_num_secs_to_sleep)
        self.assertEqual(sleeper._min_num_secs_to_sleep, min_num_secs_to_sleep)
        self.assertEqual(sleeper._max_num_secs_to_sleep, max_num_secs_to_sleep)

    def test_ctr_swaps_upper_and_lower_bounds(self):
        min_num_secs_to_sleep = 15
        max_num_secs_to_sleep = 1
        self.assertFalse(min_num_secs_to_sleep < max_num_secs_to_sleep)
        sleeper = RRSleeper(
            min_num_secs_to_sleep,
            max_num_secs_to_sleep)
        self.assertEqual(sleeper._min_num_secs_to_sleep, max_num_secs_to_sleep)
        self.assertEqual(sleeper._max_num_secs_to_sleep, min_num_secs_to_sleep)

    def test_sleep_interval_within_acceptable_range(self):
        min_num_secs_to_sleep = 1
        max_num_secs_to_sleep = 15
        self.assertTrue(min_num_secs_to_sleep < max_num_secs_to_sleep)
        sleeper = RRSleeper(min_num_secs_to_sleep, max_num_secs_to_sleep)
        for i in range(1, 1000):
            time_sleep_patch = mock.Mock()
            with mock.patch("time.sleep", time_sleep_patch):
                num_secs_slept = sleeper.sleep()
                self.assertTrue(min_num_secs_to_sleep <= num_secs_slept)
                self.assertTrue(num_secs_slept <= max_num_secs_to_sleep)
                self.assertEquals(
                    time_sleep_patch.call_args_list,
                    [mock.call(num_secs_slept)])
                time_sleep_patch.reset_mock()
