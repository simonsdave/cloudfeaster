"""..."""

import logging

import clf.queues


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

    @property
    def spider_name(self):
        return self.get("spider_name", None)

    @property
    def spider_args(self):
        return self.get("spider_args", None)

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
        pass

class CrawlResponseQueue(clf.queues.Queue):

    @classmethod
    def get_message_class(cls):
        return CrawlResponseMessage

class CrawlResponseMessage(clf.queues.Message):
    pass
