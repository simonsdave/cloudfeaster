"""This module declares :py:class:`Spider` which is an abstract base class
from which all spider classes are derived. In addition,
:py:class:`CrawlResponse` is declared."""

import hashlib
import inspect
import logging
import sys

_logger = logging.getLogger("CLF_%s" % __name__)

SC_OK = 000 + 0
SC_WALK_THREW_EXCEPTION = 400 + 1
SC_CRAWL_THREW_EXCEPTION = SC_WALK_THREW_EXCEPTION
SC_SPIDER_NOT_FOUND = 400 + 2
SC_SPIDER_CTR_THREW_EXCEPTION = 400 + 3
SC_INVALID_CRAWL_RETURN_TYPE = 400 + 4
SC_CRAWL_NOT_IMPLEMENTED = 400 + 5
SC_INVALID_CRAWL_ARG = 400 + 6
SC_BAD_CREDENTIALS = 400 + 7
SC_ACCOUNT_LOCKED_OUT = 400 + 8
SC_COULD_NOT_CONFIRM_LOGIN_STATUS = 400 + 9


class Spider(object):
    """Abstract base class for all spiders"""

    @classmethod
    def version(cls):
        """This method returns a spider's version which is  the SHA1 of
        the source code of the module containing the spider."""
        module = sys.modules[cls.__module__]
        source = inspect.getsource(module)
        sha1 = hashlib.sha1(source)
        return sha1.hexdigest()

    def __init__(self, url):
        """Constructor."""
        object.__init__(self)
        self.url = url

    def walk(self, *args):
        """This method is intended for use by the CLF infrastructure.
        Spiders should not use this method. Always returns a
        :py:class:`CrawlResponse` and won't throw an exception."""

        rv = None
        try:
            rv = self.crawl(*args)
            if type(rv) != CrawlResponse:
                status_fmt = "Invalid crawl return type '%s'. Expected '%s'"
                rv = CrawlResponse(
                    SC_INVALID_CRAWL_RETURN_TYPE,
                    status=status_fmt % (type(rv), CrawlResponse)
                )
        except Exception as ex:
            rv = CrawlResponse(SC_CRAWL_THREW_EXCEPTION, status=str(ex))

        return rv

    def crawl(self, *args):
        """Spiders should override this method to implement
        their own crawling logic.

        :param args: arguments to the crawl method - typically credentials
        :return: result of the crawl
        :rtype: :py:class:`CrawlResponse`"""

        rv = CrawlResponse(
            SC_CRAWL_NOT_IMPLEMENTED,
            status="'%s' didn't implement crawl()" % type(self).__name__
        )
        return rv


class CrawlResponse(dict):
    """Instances of this class are returned by :py:meth:`Spider.crawl` and
    :py:meth:`Spider.walk`."""

    def __init__(self, status_code, data=None, status=None):
        """Constructor.

        :param int status_code: status code
        :param data: status code
        :type dict or None
        :param status: message to describing the crawl result
        :type str or None"""

        dict.__init__(self)

        self['status_code'] = status_code
        if data:
            self['data'] = data
        if status:
            self['status'] = status

    @property
    def status_code(self):
        """
        something

        :type: int
        """
        return self.get('status_code', None)

    @property
    def data(self):
        """
        something

        :type: dict
        """
        return self.get('data', None)

    @property
    def status(self):
        """
        something

        :type: str
        """
        return self.get('status', None)
