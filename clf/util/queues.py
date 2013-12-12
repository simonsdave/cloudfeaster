"""This module defines abstract base classes for a queue
and message to be written to and read from the queue.
Messages are JSON documents.
AWS' SQS is the current queue implementation although the
details of how the queue is implemented should not leak
outside of this moduel."""

import logging
import json
import uuid

import boto
from boto.sqs.connection import SQSConnection
import jsonschema


_logger = logging.getLogger("CLF_%s" % __name__)


class Queue(object):
    """Abstract base class for all CLF queues."""

    @classmethod
    def create_queue(cls, queue_name):
        queue_name_prefix = cls.get_queue_name_prefix()
        full_queue_name = "%s%s" % (queue_name_prefix, queue_name)
        conn = SQSConnection()
        sqs_queue = conn.lookup(full_queue_name)
        if not sqs_queue:
            sqs_queue = conn.create_queue(full_queue_name)
        return cls(sqs_queue)

    @classmethod
    def get_queue(cls, queue_name):
        queue_name_prefix = cls.get_queue_name_prefix()
        full_queue_name = "%s%s" % (queue_name_prefix, queue_name)
        conn = SQSConnection()
        sqs_queue = conn.lookup(full_queue_name)
        return cls(sqs_queue) if sqs_queue else None

    @classmethod
    def get_all_queues(cls):
        conn = SQSConnection()
        sqs_queues = conn.get_all_queues()
        is_q = lambda sqs_queue: sqs_queue.name.startswith(queue_name_prefix)
        queue_name_prefix = cls.get_queue_name_prefix()
        sqs_queues = [sqs_queue for sqs_queue in sqs_queues if is_q(sqs_queue)]
        return [cls(sqs_queue) for sqs_queue in sqs_queues]

    def __init__(self, sqs_queue):
        object.__init__(self)
        self._sqs_queue = sqs_queue

    def __str__(self):
        queue_name_prefix = type(self).get_queue_name_prefix()
        return self._sqs_queue.name[len(queue_name_prefix):]

    def delete(self):
        self._sqs_queue.delete()

    def count(self):
        # this try/except block is here in case the queue is in
        # the middle of being deleted in which case queue.count()
        # will raise an exception
        try:
            return self._sqs_queue.count()
        except:
            return 0

    @classmethod
    def get_message_class(cls):
        return Message

    @classmethod
    def get_queue_name_prefix(cls):
        """Each type of queue is expected to be represented by
        its own concrete class with this class as the base class.
        SQS doesn't currently provide a way to tag queues with
        meta data as a means to describe the queue's type. Instead,
        each concrete queue class should override this method
        and choose a unique prefix for the queue's name. All of
        the details of prepending this prefix to the queue names
        will be done by this class."""
        return ""

    def read_message(self):
        sqs_messages = self._sqs_queue.get_messages(1)
        if not sqs_messages:
            return None
        sqs_message = sqs_messages[0]

        msg_class = type(self).get_message_class()

        try:
            message_body_as_dict = json.loads(sqs_message.get_body())
            schema = msg_class.get_schema()
            if schema:
                jsonschema.validate(message_body_as_dict, schema)
        except Exception as ex:
            _logger.error("Error unwrapping message '%s' - %s", sqs_message, ex)
            sqs_message.delete()
            _logger.info("Deleted invalid message '%s'", sqs_message)
            return None

        message = msg_class()
        message._message = sqs_message
        message._queue = self
        message.update(message_body_as_dict)

        return message

    def write_message(self, message):
        sqs_message = boto.sqs.message.Message()
        sqs_message.set_body(json.dumps(message))
        message._message = sqs_message
        message._queue = self

        self._sqs_queue.write(sqs_message)        

        return message

    def delete_message(self, message):
        if not message._message:
            return None
        message._message.delete()
        return message


class Message(dict):

    @classmethod
    def get_schema(cls, additional_properties=None):
        rv = {
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

        if additional_properties:
            rv["properties"].update(additional_properties)
            rv["required"].extend(additional_properties.keys())

        return rv

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

        schema = type(self).get_schema()
        property_names = schema["properties"].keys()
        for kwargs_key in kwargs.keys():
            if kwargs_key not in property_names:
                msg = "'%s' isn't one of '%s'" % (kwargs_key, property_names)
                raise TypeError(msg)

        if "uuid" not in self:
            self["uuid"] = str(uuid.uuid4())

        self._message = None
        self._queue = None

    def delete(self):
        return self._queue.delete_message(self) if self._queue else None

    def __getattr__(self, name):
        schema = type(self).get_schema()
        property_names = schema["properties"].keys()
        if name not in property_names:
            msg = "'%s' isn't one of '%s'" % (name, property_names)
            raise AttributeError(msg)
        return self.get(name, None)
