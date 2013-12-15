"""This module contains unit tests for the ```clf.queues``` module."""

import unittest
import uuid

import mock

from clf.util.queues import Message
from clf.util.queues import Queue

class DaveQueue(Queue):
    """Super simple Queue to be used for testing the queue name
    prefix functionality works as desired."""

    queue_name_prefix = "dave_"

    @classmethod
    def get_queue_name_prefix(cls):
        return cls.queue_name_prefix

class TestQueue(unittest.TestCase):

    def test_create_queue_queue_already_exists(self):
        queue_name = str(uuid.uuid4())
        expected_queue_name = DaveQueue.queue_name_prefix + queue_name

        mock_existing_queue = mock.Mock()
        mock_lookup_method = mock.Mock(return_value=mock_existing_queue)
        name_of_method_to_patch = "boto.sqs.connection.SQSConnection.lookup"
        with mock.patch(name_of_method_to_patch, mock_lookup_method):

            mock_create_queue_method = mock.Mock()
            name_of_method_to_patch = "boto.sqs.connection.SQSConnection.create_queue"
            with mock.patch(name_of_method_to_patch, mock_create_queue_method):
                queue = DaveQueue.create_queue(queue_name)
                self.assertIsNotNone(queue)
                self.assertEqual(queue._sqs_queue, mock_existing_queue)
            self.assertEqual(mock_create_queue_method.call_args_list, [])

        self.assertEqual(
            mock_lookup_method.call_args_list,
            [mock.call(expected_queue_name)])

    def test_create_queue_queue_does_not_already_exists(self):
        queue_name = str(uuid.uuid4())
        expected_queue_name = DaveQueue.queue_name_prefix + queue_name

        mock_lookup_method = mock.Mock(return_value=None)
        name_of_method_to_patch = "boto.sqs.connection.SQSConnection.lookup"
        with mock.patch(name_of_method_to_patch, mock_lookup_method):

            mock_new_queue = mock.Mock()
            mock_create_queue_method = mock.Mock(return_value=mock_new_queue)
            name_of_method_to_patch = "boto.sqs.connection.SQSConnection.create_queue"
            with mock.patch(name_of_method_to_patch, mock_create_queue_method):
                queue = DaveQueue.create_queue(queue_name)
                self.assertIsNotNone(queue)
                self.assertEqual(queue._sqs_queue, mock_new_queue)
            self.assertEqual(
                mock_create_queue_method.call_args_list,
                [mock.call(expected_queue_name)])

        self.assertEqual(
            mock_lookup_method.call_args_list,
            [mock.call(expected_queue_name)])

    def tests_get_queue_all_ok(self):
        queue_name = str(uuid.uuid4())
        mock_queue = mock.Mock()
        mock_lookup_method = mock.Mock(return_value=mock_queue)
        name_of_method_to_patch = "boto.sqs.connection.SQSConnection.lookup"
        with mock.patch(name_of_method_to_patch, mock_lookup_method):
            queue = Queue.get_queue(queue_name)
            self.assertIsNotNone(queue)
            self.assertIsInstance(queue, Queue)
            self.assertEqual(queue._sqs_queue, mock_queue)
        self.assertIsNone(mock_lookup_method.assert_called_once_with(queue_name))

    def tests_get_queue_queue_not_found(self):
        queue_name = str(uuid.uuid4())
        mock_lookup_method = mock.Mock(return_value=None)
        name_of_method_to_patch = "boto.sqs.connection.SQSConnection.lookup"
        with mock.patch(name_of_method_to_patch, mock_lookup_method):
            queue = Queue.get_queue(queue_name)
            self.assertIsNone(queue)
        self.assertIsNone(mock_lookup_method.assert_called_once_with(queue_name))

    def tests_get_all_queues(self):
        mock_queues = [mock.Mock(), mock.Mock(), mock.Mock()]
        mock_get_all_queues_method = mock.Mock(return_value=mock_queues)
        name_of_method_to_patch = "boto.sqs.connection.SQSConnection.get_all_queues"
        with mock.patch(name_of_method_to_patch, mock_get_all_queues_method):
            queues = Queue.get_all_queues()
            self.assertIsNotNone(queues)
            self.assertEqual(len(queues), len(mock_queues))
            for (queue, mock_queue) in zip(queues, mock_queues):
                self.assertIsNotNone(queue)
                self.assertIsInstance(queue, Queue)
                self.assertEqual(queue._sqs_queue, mock_queue)
        self.assertIsNone(mock_get_all_queues_method.assert_called_once_with())

    def test_ctr(self):
        mock_sqs_queue = mock.Mock()
        queue = Queue(mock_sqs_queue)
        self.assertEqual(queue._sqs_queue, mock_sqs_queue)

    def test_str(self):
        mock_sqs_queue = mock.Mock()
        mock_sqs_queue.name = str(uuid.uuid4())
        queue = Queue(mock_sqs_queue)
        self.assertEqual(str(queue), mock_sqs_queue.name)

    def test_delete(self):
        mock_sqs_queue = mock.Mock()
        queue = Queue(mock_sqs_queue)
        queue.delete()
        self.assertIsNone(mock_sqs_queue.delete.assert_called_once_with())

    def test_count_all_ok(self):
        mock_sqs_queue = mock.Mock()
        mock_count_return_value = mock.Mock()
        mock_sqs_queue.count.return_value = mock_count_return_value
        queue = Queue(mock_sqs_queue)
        count = queue.count()
        self.assertIsNone(mock_sqs_queue.count.assert_called_once_with())
        self.assertEqual(count, mock_count_return_value)

    def test_count_on_sqs_exception(self):
        mock_sqs_queue = mock.Mock()
        mock_sqs_queue.count.side_effect = Exception()
        queue = Queue(mock_sqs_queue)
        count = queue.count()
        self.assertIsNone(mock_sqs_queue.count.assert_called_once_with())
        self.assertEqual(count, 0)

    def test_get_message_class(self):
        self.assertEqual(Queue.get_message_class(), Message)

    def test_read_message_all_ok(self):
        pass

    def test_write_message_all_ok(self):
        pass


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

    def test_get_schema_no_additional_properties(self):
        expected_schema = {
            "type": "object",
            "properties": {
                "uuid": {
                    "type": "string",
                    "minLength": 1,
                },
            },
            "required": [
                "uuid",
            ],
            "additionalProperties": False,
        }
        self.assertEqual(expected_schema, Message.get_schema())

    def test_get_schema_with_additional_properties(self):
        expected_schema = {
            "type": "object",
            "properties": {
                "uuid": {
                    "type": "string",
                    "minLength": 1,
                },
                "spider_name": {
                    "type": "string",
                    "minLength": 1,
                },
                "spider_args": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "minLength": 1,
                    },
                },
            },
            "required": [
                "uuid",
                "spider_name",
                "spider_args",
            ],
            "additionalProperties": False,
        }

        additional_props = {
            "spider_name": {
                "type": "string",
                "minLength": 1,
            },
            "spider_args": {
                "type": "array",
                "items": {
                    "type": "string",
                    "minLength": 1,
                },
            },
        }
        self.assertEqual(expected_schema, Message.get_schema(additional_props))
