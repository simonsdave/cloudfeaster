"""..."""

import logging

import clf.queues
import clf.spider


_logger = logging.getLogger("CLF_%s" % __name__)


class CrawlRequestQueue(clf.queues.Queue):

    @classmethod
    def get_message_class(cls):
        return CrawlRequestMessage

class CrawlRequestMessage(clf.queues.Message):

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
        return clf.queues.Message.get_schema(additional_properties)

    def process(self):
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
        crawl_response_status_code = clf.spider.SC_SPIDER_NOT_FOUND
        crawl_response = clf.spider.CrawlResponse(crawl_response_status_code)
        crawl_response_message = CrawlResponseMessage(
            uuid=self.uuid,
            spider_name=self.spider_name,
            spider_args=self.spider_args,
            crawl_response=crawl_response)
        return crawl_response_message

class CrawlResponseQueue(clf.queues.Queue):

    @classmethod
    def get_message_class(cls):
        return CrawlResponseMessage

class CrawlResponseMessage(clf.queues.Message):

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
        return clf.queues.Message.get_schema(additional_properties)
