"""This module contains the clparserutil's unit tests."""

import logging
import optparse
import unittest

from clf.util import clparserutil


class TestCase(unittest.TestCase):

    def test_check_couchdb(self):
        option = clparserutil.Option(
            "--create",
            action="store",
            dest="couchdb",
            default="bindle:8909/berry",
            type="couchdb",
            help="whatever")
        values = [
            ["bindle:8909/berry", "bindle:8909/berry"],
            ["b:8/y", "b:8/y"],

            ["dave", None],
            ["dave:89", None],
            ["89/", None],
            ["dave:89/", None],
        ]
        type_checker = clparserutil.Option.TYPE_CHECKER["couchdb"]
        self.assertIsNotNone(type_checker)
        opt_string = option.get_opt_string(),
        for value in values:
            if value[1] is not None:
                msg = "Failed to parse '%s' correctly." % value[0]
                result = type_checker(option, opt_string, value[0])
                self.assertEqual(result, value[1], msg)
            else:
                with self.assertRaises(optparse.OptionValueError):
                    type_checker(option, opt_string, value[0])

    def test_check_logginglevel(self):
        option = clparserutil.Option(
            "--create",
            action="store",
            dest="logging_level",
            default=logging.FATAL,
            type="logginglevel",
            help="whatever")
        values = [
            ["debug", logging.DEBUG],
            ["info", logging.INFO],
            ["INFO", logging.INFO],
            ["warning", logging.WARNING],
            ["eRRor", logging.ERROR],
            ["CRITICAL", logging.CRITICAL],
            ["FATAL", logging.FATAL],

            ["dave", None],
            ["None", None],
            ["", None],
        ]
        type_checker = clparserutil.Option.TYPE_CHECKER["logginglevel"]
        self.assertIsNotNone(type_checker)
        opt_string = option.get_opt_string(),
        for value in values:
            if value[1] is not None:
                msg = "Failed to parse '%s' correctly." % value[0]
                result = type_checker(option, opt_string, value[0])
                self.assertEqual(result, value[1], msg)
            else:
                with self.assertRaises(optparse.OptionValueError):
                    type_checker(option, opt_string, value[0])

    def test_check_host_colon_port(self):
        option = clparserutil.Option(
            "--create",
            action="store",
            dest="server",
            default="bindle:8909",
            type="hostcolonport",
            help="whatever")
        values = [
            ["bindle:8909", "bindle:8909"],
            ["b:8", "b:8"],

            ["dave", None],
            ["89", None],
            [":89", None],
        ]
        type_checker = clparserutil.Option.TYPE_CHECKER["hostcolonport"]
        self.assertIsNotNone(type_checker)
        opt_string = option.get_opt_string(),
        for value in values:
            if value[1] is not None:
                msg = "Failed to parse '%s' correctly." % value[0]
                result = type_checker(option, opt_string, value[0])
                self.assertEqual(result, value[1], msg)
            else:
                with self.assertRaises(optparse.OptionValueError):
                    type_checker(option, opt_string, value[0])

    def test_check_memcached(self):
        option = clparserutil.Option(
            "--memcached",
            action="store",
            dest="cluster",
            default="localhost:8909",
            type="memcached",
            help="whatever")
        values = [
            ["bindle:8909", ["bindle:8909"]],
            ["b:8, d:89", ["b:8", "d:89"]],
            ["b:8 , d:89", ["b:8", "d:89"]],
            [" b:8 ,d:89", ["b:8", "d:89"]],

            ["dave", None],
            ["89", None],
            [":89", None],
        ]
        type_checker = clparserutil.Option.TYPE_CHECKER["memcached"]
        self.assertIsNotNone(type_checker)
        opt_string = option.get_opt_string(),
        for value in values:
            if value[1] is not None:
                msg = "Failed to parse '%s' correctly." % value[0]
                result = type_checker(option, opt_string, value[0])
                self.assertEqual(result, value[1], msg)
            else:
                with self.assertRaises(optparse.OptionValueError):
                    type_checker(option, opt_string, value[0])

    def test_check_boolean(self):
        option = clparserutil.Option(
            "--create",
            action="store",
            dest="create",
            default=True,
            type="boolean",
            help="create key store - default = True")
        values = [
            ["true", True],
            ["True", True],
            ["trUe", True],
            ["t", True],
            ["T", True],
            ["1", True],
            ["y", True],
            ["yes", True],
            ["y", True],

            ["false", False],
            ["False", False],
            ["FaLse", False],
            ["f", False],
            ["F", False],
            ["0", False],
            ["f", False],
            ["no", False],
            ["n", False],

            ["dave", None],
            ["None", None],
            ["", None],
        ]
        type_checker = clparserutil.Option.TYPE_CHECKER["boolean"]
        opt_string = option.get_opt_string(),
        for value in values:
            if value[1] is not None:
                msg = "Failed to parse '%s' correctly." % value[0]
                result = type_checker(option, opt_string, value[0])
                self.assertEqual(result, value[1], msg)
            else:
                with self.assertRaises(optparse.OptionValueError):
                    type_checker(option, opt_string, value[0])
