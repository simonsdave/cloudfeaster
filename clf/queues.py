"""..."""

import logging
import json
import uuid

from boto.sqs.connection import SQSConnection
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

    def count(self):
        # this try/except block is here in case the queue is in
        # the middle of being deleted in which case queue.count()
        # will raise an exception
        try:
            return self.sqs_queue.count()
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
