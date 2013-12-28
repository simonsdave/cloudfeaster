"""This module contains all queues and messages used by a spider host."""

import datetime
import logging

from clf.util.queues import Queue
from clf.util.queues import Message
import clf.spider

_logger = logging.getLogger("CLF_%s" % __name__)


class SpiderHostQueue(Queue):
    """An abstract base class for spider host request and response
    queues. This class exists because we wanted a single location
    to encapsulate all the details of encrypting and decrypting
    the spider_args property of crawl requests and responses."""

    def write_message(self, message):
        """Overrides the default implementation of
        :py:meth:`clf.util.queues.Queue.write_message`
        to encrypt the message's "spider_args" property
        before the message is written to the queue.

        :param message: write this message to the queue
        :type message: :py:class:`CrawlRequest`
        :return: see :py:meth:`clf.util.queues.Queue.write_message`
        :rtype: see :py:meth:`clf.util.queues.Queue.write_message`"""
        self._encrypt_all_spider_args(message)
        return Queue.write_message(self, message)

    def _encrypt_all_spider_args(self, message):
        if not message:
            return message

        spider_args = message.get("spider_args", [])
        for i in range(0, len(spider_args)):
            spider_args[i] = self._encrypt_spider_arg(spider_args[i])

        return message

    def _encrypt_spider_arg(self, spider_arg):
        return spider_arg

    def read_message(self):
        """Overrides the default implementation of
         :py:meth:`clf.util.queues.Queue.read_message`
        to decrypt the message's "spider_args" property
        after the message is read from the queue.

        :return: A message if one is available otherwise None.
        :rtype: :py:class:`Message`"""
        message = Queue.read_message(self)
        self._decrypt_all_spider_args(message)
        return message

    def _decrypt_all_spider_args(self, message):
        if not message:
            return message

        spider_args = message.get("spider_args", [])
        for i in range(0, len(spider_args)):
            spider_args[i] = self._decrypt_spider_arg(spider_args[i])

        return message

    def _decrypt_spider_arg(self, spider_arg):
        return spider_arg


class SpiderHostMessage(Message):
    """An abstract base class for spider host request and response
    messages. This class exists only because :py:class:`SpiderHostQueue`
    was created and, since all spider host queues had a common abstract
    base class it just felt like the right (symmetrical) thing to do
    to have an abstract base class for all spider host messages."""
    pass


class CrawlRequestQueue(SpiderHostQueue):
    """Spider hosts read crawl requests from an instance
    of :py:class:`CrawlRequestQueue`."""

    @classmethod
    def get_message_class(cls):
        return CrawlRequest

    @classmethod
    def get_queue_name_prefix(cls):
        return "clf_creq_"


class CrawlRequest(SpiderHostMessage):
    """An instance of :py:class:`CrawlRequest` represents
    a request for a spider to crawl a web site. After the request has been
    created it is added to a :py:class:`CrawlRequestQueue`.
    A spider host reads the request from the
    :py:class:`CrawlRequestQueue`, calls
    :py:class:`CrawlRequest.process` and writes the response
    to a :py:class:`CrawlResponseQueue`."""

    @classmethod
    def get_schema(cls):
        schema = {
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
        return schema

    # :TODO: might be interesting to not have to pass local_spider_repo
    # but rather construct the local spider repo on the fly by reading
    # the remote spider repo's name from a configuration file.

    def process(self, local_spider_repo):
        metrics = {}

        download_spider_start_time = datetime.datetime.utcnow()
        spider_class = local_spider_repo.get_spider_class(self.spider_name)
        download_spider_end_time = datetime.datetime.utcnow()

        self._add_timing_entry_to_metrics_dict(
            metrics,
            download_spider_start_time,
            download_spider_end_time,
            "download_spider")

        if not spider_class:
            status = "Unknown spider '%s'" % self.spider_name
            crawl_response = clf.spider.CrawlResponse(
                clf.spider.SC_SPIDER_NOT_FOUND,
                status=status
            )
            rv = CrawlResponse(
                uuid=self.uuid,
                spider_name=self.spider_name,
                spider_args=self.spider_args,
                crawl_response=crawl_response,
                metrics=metrics)
            return rv

        spider = spider_class()

        crawl_start_time = datetime.datetime.utcnow()
        crawl_response = spider.walk(*self.spider_args)
        crawl_end_time = datetime.datetime.utcnow()

        self._add_timing_entry_to_metrics_dict(
            metrics,
            crawl_start_time,
            crawl_end_time,
            "crawl")

        crawl_response = CrawlResponse(
            uuid=self.uuid,
            spider_name=self.spider_name,
            spider_version=spider_class.version(),
            spider_args=self.spider_args,
            crawl_response=crawl_response,
            metrics=metrics)

        return crawl_response

    def _add_timing_entry_to_metrics_dict(
        self,
        metrics,
        start_time,
        end_time,
        key_prefix):

        """process() collects a bunch of timing information during
        its execution. This method creates metrics from this raw information
        and adds those metrics to a dict which can be incorporated into
        the crawl response as timing/performance info."""

        # start time date in RFC 2822 format (same value as Date HTTP header)
        # ex "Thu, 28 Jun 2001 14:17:15 +0000"
        date_fmt = "%a, %d %b %Y %H:%M:%S +0000"
        start_time_key = "%s_start_time" % key_prefix
        metrics[start_time_key] = start_time.strftime(date_fmt)

        duration = end_time - start_time
        duration_in_seconds = round(duration.total_seconds(), 2)
        duration_key = "%s_time_in_seconds" % key_prefix
        metrics[duration_key] = duration_in_seconds


class CrawlResponseQueue(SpiderHostQueue):
    """After a :py:class:`CrawlRequest` is processed by
    a spider host, the spider host creates an instance of
    :py:class:`CrawlResponse` in response to the request
    and adds the :py:class:`CrawlResponse`
    to a :py:class:`CrawlResponseQueue`."""

    @classmethod
    def get_message_class(cls):
        return CrawlResponse

    @classmethod
    def get_queue_name_prefix(cls):
        return "clf_cres_"


class CrawlResponse(SpiderHostMessage):

    @classmethod
    def get_schema(cls):
        schema = {
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
                "spider_version": {
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
            },
            "required": [
                "uuid",
                "spider_name",
                "spider_args",
                "crawl_response",
                "metrics",
            ],
            "additionalProperties": False,
        }
        return schema
