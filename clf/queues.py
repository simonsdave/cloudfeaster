"""..."""

import logging
import json
import uuid

import boto
from boto.sqs.connection import SQSConnection
import jsonschema

import clf.jsonschemas


_logger = logging.getLogger("CLF_%s" % __name__)


class Queue(object):

    @classmethod
    def create_queue(cls, queue_name):
        conn = SQSConnection()
        sqs_queue = conn.lookup(queue_name)
        if not sqs_queue:
            sqs_queue = conn.create_queue(queue_name)
        return cls(sqs_queue)

    @classmethod
    def get_queue(cls, queue_name):
        conn = SQSConnection()
        sqs_queue = conn.lookup(queue_name)
        return cls(sqs_queue) if sqs_queue else None

    @classmethod
    def get_all_queues(cls):
        conn = SQSConnection()
        return [cls(sqs_queue) for sqs_queue in conn.get_all_queues()]

    def __init__(self, sqs_queue):
        object.__init__(self)
        self._sqs_queue = sqs_queue

    def __str__(self):
        return self._sqs_queue.name

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
    def get_schema(cls):
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
        return rv

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

        if "uuid" not in self:
            self["uuid"] = str(uuid.uuid4())

        self._message = None
        self._queue = None

    def delete(self):
        return self._queue.delete_message(self) if self._queue else None

    @property
    def uuid(self):
        return self.get("uuid", None)
