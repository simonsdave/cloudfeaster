"""This module contains all queues and messages used by a spider host."""

import logging

from clf.util.queues import Queue
from clf.util.queues import Message
import clf.spider

_logger = logging.getLogger("CLF_%s" % __name__)


class CrawlRequestQueue(Queue):

    @classmethod
    def get_message_class(cls):
        return CrawlRequest

    @classmethod
    def get_queue_name_prefix(cls):
        return "clf_creq_"


class CrawlRequest(Message):
    """An instance of :py:class:`clf.spider_host.CrawlRequest` represents a request
    for a spider to crawl a web site. After the request has been created
    it is added to a ```CrawlRequestQueue```. A spider host will read
    the request from the ```CrawlRequestQueue``` and write the response
    to a :py:class:`clf.spider_host.CrawlResponseQueue`."""

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
        required_properties = [
            "spider_name",
            "spider_args",
        ]
        return Message.get_schema(additional_properties, required_properties)

    # :TODO: might be interesting to not have to pass local_spider_repo
    # but rather construct the local spider repo on the fly by reading
    # the remote spider repo's name from a configuration file.

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
    """After a :py:class:`clf.spider_host.CrawlRequest` is processed by a spider host,
    the spider host creates an instance of :py:class:`clf.spider_host.CrawlResponse`
    in response to the request and adds the :py:class:`clf.spider_host.CrawlResponse`
    to a :py:class:`clf.spider_host.CrawlResponseQueue`."""

    @classmethod
    def get_message_class(cls):
        return CrawlResponse

    @classmethod
    def get_queue_name_prefix(cls):
        return "clf_cres_"


class CrawlResponse(Message):

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
            "metrics": {
                "type": "object",
            },
        }

        required_properties = [
            "spider_name",
            "spider_args",
            "crawl_response",
            "metrics",
        ]

        rv = Message.get_schema(additional_properties, required_properties)
        return rv
