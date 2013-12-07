"""..."""

import logging

from clf.util.queues import Queue
from clf.util.queues import Message
import clf.spider


_logger = logging.getLogger("CLF_%s" % __name__)


class CrawlRequestQueue(Queue):

    @classmethod
    def get_message_class(cls):
        return CrawlRequestMessage

class CrawlRequestMessage(Message):

    @classmethod
    def get_schema(cls):
        additional_properties = {
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
        return Message.get_schema(additional_properties)

    def process(self, local_spider_repo):
        spider_class = local_spider_repo.get_spider_class(self.spider_name)
        spider = spider_class()
        return spider.walk(*self.spider_args)

class CrawlResponseQueue(Queue):

    @classmethod
    def get_message_class(cls):
        return CrawlResponseMessage

class CrawlResponseMessage(Message):

    @classmethod
    def get_schema(cls):
        additional_properties = {
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
            "crawl_response": {
                "type": "object",
            },
        }
        return Message.get_schema(additional_properties)
