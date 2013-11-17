"""..."""

import logging
import json
import uuid

import boto.sqs.connection
import jsonschema

import clf.jsonschemas


_logger = logging.getLogger("CLF_%s" % __name__)

class Message(dict):

    def __init__(self, sqs_message):
        object.__init__(self)
        self._sqs_message = sqs_message

        try:
            message_body = _sqs_message.get_body()
            message_body_as_dict = json.loads(message_body)
#            jsonschema.validate(
#                message_body_as_dict,
#                clf.jsonschemas.crawl_request)
            object.__init__(self, message_body_as_dict)
        except Exception as ex:
            object.__init__(self)
            _logger.error(
                "Error processing message '%s' - %s",
                message_body,
                str(ex))

class Queue(object):

    _conn = None

    @classmethod
    def _get_conn(cls):
        if not cls._conn:
            cls._conn = boto.sqs.connection.SQSConnection()
        return cls._conn

    @classmethod
    def create_queue(cls, queue_name):
        queue = cls.get_queue(queue_name)
        if not queue:
            queue = cls(cls._get_conn().create_queue(queue_name))
        return queue

    @classmethod
    def get_queue(cls, queue_name):
        sqs_queue = cls._get_conn().lookup(queue_name)
        return cls(sqs_queue) if sqs_queue else None

    @classmethod
    def get_all_queues(cls):
        return [cls(sqs_queue) for sqs_queue in cls._get_conn().get_all_queues()]

    def __init__(self, sqs_queue):
        object.__init__(self)
        self._sqs_queue = sqs_queue

    def __str__(self):
        return self._sqs_queue.name

    def count(self):
        # this try/except block is here in case the queue is in
        # the middle of being deleted in which case queue.count()
        # will raise an exception
        try:
            return queue.count()
        except:
            return 0

    def get_messages(self, num_messages=1):
        sqs_messages = self._sqs_queue.get_messages(num_messages)
        return [Message(sqs_message) for sqs_message in sqs_messages]
        
    def get_message(self):
        messages = self.get_messages(1)
        return messages[0] if len(messages) else None

    def delete(self):
        self._sqs_queue.delete()

class CrawlRequestQueue(Queue):

    def write_message(self, spider_name, spider_args):
        message_body_as_dict = {
            "uuid": str(uuid.uuid4()),
            "spider": spider_name,
            "args": spider_args,
        }
        message_body_as_json_doc = json.dumps(message_body_as_dict)
        # :TODO: validate JSON doc against JSON schema
        message = boto.sqs.message.Message()
        message.set_body(message_body_as_json_doc)

        queue.write(message)        

        return Crawl


class CrawlResponseQueue(Queue):
    pass
