"""..."""

import logging

import clf.queues


_logger = logging.getLogger("CLF_%s" % __name__)


class CrawlRequestQueue(clf.queues.CrawlRequestQueue):

    @classmethod
    def get_message_class(cls):
        return CrawlRequestMessage

class CrawlRequestMessage(clf.queues.CrawlRequestMessage):

    def process(self):
        pass

class CrawlResponseQueue(clf.queues.CrawlResponseQueue):

    @classmethod
    def get_message_class(cls):
        return CrawlResponseMessage

class CrawlResponseMessage(clf.queues.Message):
    pass
