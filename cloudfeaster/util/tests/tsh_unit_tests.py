"""This module contains a collection of unit tests which
validate clf.util.tsh"""

import signal
import unittest

import mock

from .. import tsh


class TSHTestCase(unittest.TestCase):

    def test_value_is_none(self):
        signal_dot_signal_patch = mock.Mock()
        with mock.patch("signal.signal", signal_dot_signal_patch):
            tsh.install()
        self.assertEquals(
            signal_dot_signal_patch.call_args_list,
            [mock.call(signal.SIGINT, tsh._term_signal_handler)])

    def test_term_signal_handler_calls_sys_dot_exit(self):
        sys_dot_exit_patch = mock.Mock()
        with mock.patch("sys.exit", sys_dot_exit_patch):
            frame = "what should this be?"
            tsh._term_signal_handler(signal.SIGINT, frame)
        self.assertEquals(
            sys_dot_exit_patch.call_args_list,
            [mock.call(0)])
