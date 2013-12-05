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
        # get spider name from self
        # create spider repo. where does spider repo's name come from?
        # download spider from spider repo to temp file
        # import temp file as python module
        # module should contain a single class that derives from clf.Spider
        #   so create instance of that spider (no ctr arguments)
        # call spider's walk() method using args from self
        # walk() return value is this method's return value.
        #
        # this method should not throw an exception
        spider_class = local_spider_repo.get_spider_class(self.spider_name)

        crawl_response_status_code = clf.spider.SC_SPIDER_NOT_FOUND
        crawl_response = clf.spider.CrawlResponse(crawl_response_status_code)
        crawl_response_message = CrawlResponseMessage(
            uuid=self.uuid,
            spider_name=self.spider_name,
            spider_args=self.spider_args,
            crawl_response=crawl_response)
        return crawl_response_message

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
