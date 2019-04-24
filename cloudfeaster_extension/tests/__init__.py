"""This module contains unit tests for the ```cloudfeaster_extension``` module."""

import unittest
import uuid

import mock

import cloudfeaster_extension


class TestCloudfeasterExtension(unittest.TestCase):

    def test_send_keys(self):
        my_patch = mock.Mock()
        with mock.patch('selenium.webdriver.remote.webelement.WebElement.send_keys', my_patch):
            paranoia_level = uuid.uuid4().hex
            webelement = uuid.uuid4().hex
            value = uuid.uuid4().hex

            cloudfeaster_extension.send_keys(paranoia_level, webelement, value)

            my_patch.called_once_with(webelement, value)

    def test_user_agent(self):
        user_agent = cloudfeaster_extension.user_agent()
        self.assertTrue(user_agent)

    def test_proxy(self):
        paranoia_level = uuid.uuid4().hex
        (host, port) = cloudfeaster_extension.proxy(paranoia_level)
        self.assertIsNone(host)
        self.assertIsNone(port)
