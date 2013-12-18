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

    @classmethod
    def get_queue_name_prefix(cls):
        return "clf_creq_"


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
        if not spider_class:
            status = "Unknown spider '%s'" % self.spider_name
            rv = clf.spider.CrawlResponse(
                clf.spider.SC_SPIDER_NOT_FOUND,
                status=status
            )
            return rv
        spider = spider_class()
        return spider.walk(*self.spider_args)


class CrawlResponseQueue(Queue):

    @classmethod
    def get_message_class(cls):
        return CrawlResponseMessage

    @classmethod
    def get_queue_name_prefix(cls):
        return "clf_cres_"


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
