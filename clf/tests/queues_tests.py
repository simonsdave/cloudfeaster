"""This module contains unit tests for the ```clf.queues``` module."""

import unittest
import uuid

import mock

from clf.queues import Message

class TestMessage(unittest.TestCase):

    def test_ctr_with_no_args(self):
        m = Message()
        self.assertIsNotNone(m)
        self.assertEquals(1, len(m))
        self.assertIn("uuid", m)
        self.assertIsInstance(m["uuid"], str)
        self.assertTrue(1 <= len(m["uuid"]))

    def test_ctr_raises_exception_on_bad_property_name(self):
        regexp = "'dave' isn't one of '\['uuid'\]'"
        with self.assertRaisesRegexp(TypeError, regexp):
            Message(dave=42)

    def test_delete_returns_none_when_queue_not_set(self):
        m = Message()
        self.assertIsNone(m.delete())

    def test_delete_calls_queue_delete_message(self):
        m = Message()
        mock_queue = mock.Mock()
        delete_message_return_value = uuid.uuid4()
        mock_queue.delete_message.return_value = delete_message_return_value
        m._queue = mock_queue
        self.assertEqual(delete_message_return_value, m.delete())
        self.assertEqual(
            mock_queue.delete_message.call_args_list,
            [mock.call(m)])

    def test__getattr__all_good_with_message_class(self):
        m = Message()
        self.assertEqual(m.uuid, m["uuid"])

    def test__getattr__unknown_attribute_with_message_class(self):
        m = Message()
        regexp = "'dave' isn't one of '\['uuid'\]'"
        with self.assertRaisesRegexp(AttributeError, regexp):
            m.dave

    def test__getattr__all_good_with_class_derived_from_message(self):
        class MyMessage(Message):
            @classmethod
            def get_schema(cls):
                rv = Message.get_schema()
                properties = rv["properties"]
                properties["spider_name"] = {
                    "type": "string",
                    "minLength": 1,
                }
                required = rv["required"]
                required.append("spider_name")
                return rv
        spider_name = uuid.uuid4()
        m = MyMessage(spider_name=spider_name)
        self.assertEqual(m.spider_name, m["spider_name"])
