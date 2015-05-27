"""This module defines the core CLF spidering API.
For example, a spider author creates a spider by
creating a new class which derives from :py:class:`Spider`.
Next the spider author implements a :py:meth:`Spider.crawl`
which returns an instance of :py:class:`CrawlResponse`.
Both :py:class:`Spider` and :py:class:`CrawlResponse`
are defined in this module.
"""

import getpass
import hashlib
import inspect
import json
import logging
import os
import re
import sets
import sys

import jsonschema

_logger = logging.getLogger(__name__)


def _load_spider_metadata_jsonschema():
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    filename = os.path.join(directory, "spider_metadata.json")
    with open(filename) as fp:
        return json.load(fp)


class Spider(object):
    """Abstract base class for all spiders"""

    """Used to validate return value of ```metadata()```."""
    _metadata_jsonschema = _load_spider_metadata_jsonschema()

    @classmethod
    def _get_crawl_method_arg_names(cls):
        """Returns the list of argument names for
        :py:meth:`Spider.crawl`. If the spider doesn't
        have a crawl method return None.
        """
        def is_crawl_instance_method(t):
            if not inspect.ismethod(t):
                return False
            if inspect.isclass(t.__self__):
                return False
            if t.__module__ != cls.__module__:
                return False
            return t.__name__ == "crawl"

        for (_, t) in inspect.getmembers(cls, is_crawl_instance_method):
            return inspect.getargspec(t).args[1:]

        return None

    @classmethod
    def get_validated_metadata(cls):
        """Spiders supply their metadata by overriding
        :py:meth:`Spider.get_metadata` and
        those wishing to retrieve a spider's metadata
        should call this method. This method validates
        and potentially modifies the metadata returned
        by :py:meth:`Spider.get_metadata`
        to add aspects of the metadata which can be
        determined by inspecting the spider's source code.
        """
        metadata = cls.get_metadata()

        try:
            jsonschema.validate(metadata, cls._metadata_jsonschema)
        except Exception as ex:
            raise SpiderMetadataError(cls, ex=ex)

        crawl_method_arg_names = cls._get_crawl_method_arg_names()
        if crawl_method_arg_names is None:
            message_detail = "crawl() method arg names not found"
            raise SpiderMetadataError(cls, message_detail=message_detail)

        identifying_factors = metadata.get("identifying_factors", {})
        authenticating_factors = metadata.get("authenticating_factors", {})

        factors = list(identifying_factors.keys())
        factors.extend(authenticating_factors.keys())

        if sets.Set(factors) != sets.Set(crawl_method_arg_names):
            message_detail = "crawl() arg names and factor names don't match"
            raise SpiderMetadataError(cls, message_detail=message_detail)

        factor_display_order = metadata.get("factor_display_order", None)
        if factor_display_order is None:
            metadata["factor_display_order"] = crawl_method_arg_names
        else:
            if sets.Set(factors) != sets.Set(factor_display_order):
                message_detail = "factors and factor display order don't match"
                raise SpiderMetadataError(cls, message_detail=message_detail)

        ttl = metadata.get("ttl", "0s")
        reg_ex_pattern = "(?P<value>\d+)(?P<unit>[dhms])"
        reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
        match = reg_ex.match(ttl)
        assert match
        value = int(match.group("value"))
        unit = match.group("unit").lower()
        multipliers = {
            "d": 24 * 60 * 60,
            "h": 60 * 60,
            "m": 60,
            "s": 1,
        }
        metadata["ttl"] = value * multipliers[unit]

        return metadata

    @classmethod
    def get_metadata(cls):
        """Spider classes should override this method to return
        a dict represention of a JSON document which describes the
        spider.

        See the sample spiders for a broad variety of metadata
        examples.
        """
        fmt = "%s must implememt class method 'get_metadata()'"
        raise NotImplementedError(fmt % cls)

    @property
    def url(self):
        """Returns the URL that the spider will crawl."""
        metadata = type(self).get_validated_metadata()
        return metadata.get("url", None)

    @classmethod
    def version(cls):
        """This method returns a spider's version which is  the SHA1 of
        the source code of the module containing the spider.
        """
        module = sys.modules[cls.__module__]
        source = inspect.getsource(module)
        sha1 = hashlib.sha1(source)
        return sha1.hexdigest()

    def crawl(self, *args):
        """Spiders should override this method to implement
        their own crawling logic.

        :param args: crawl arguments
        :return: result of the crawl
        :rtype: :py:class:`CrawlResponse`
        :raises Exception: this method may raises exceptions
        """
        fmt = "%s must implememt crawl()"
        raise NotImplementedError(fmt % self)

    # :TODO: choose a different name for this method
    @classmethod
    def walk(cls, *args):
        """:py:meth:`Spider.crawl` can be used to run spiders. This approach
        works perfectly well. :py:meth:`Spider.walk` also calls
        :py:meth:`Spider.crawl` to run the spider and also does things like
        use the spider's metadata to validate crawl args before calling
        :py:meth:`Spider.crawl`, catches any exceptions :py:meth:`Spider.crawl`
        raises and verifies that the return type from :py:meth:`Spider.crawl`
        is a :py:class:`CrawlResponse`.

        :param args: crawl arguments
        :return: result of the crawl - never raises an exception
        :rtype: :py:class:`CrawlResponse`
        """
        spider = None
        try:
            spider = cls()
        except Exception as ex:
            crawl_response = CrawlResponseCtrRaisedException(ex)

        if spider is not None:
            try:
                crawl_response = spider.crawl(*args)
            except Exception as ex:
                crawl_response = CrawlResponseCrawlRaisedException(ex)

        if not isinstance(crawl_response, CrawlResponse):
            crawl_response = CrawlResponseInvalidCrawlReturnType(crawl_response)

        return crawl_response


class SpiderMetadataError(Exception):
    """Raised by :py:meth:`Spider.get_validated_metadata` to indicate
    that :py:meth:`Spider.get_metadata` returned invalid metadata.
    """

    def __init__(self, spider_class, message_detail=None, ex=None):
        fmt = "Spider class '%s' has invalid metadata"
        message = fmt % spider_class.__name__

        if message_detail:
            message = "%s - %s" % (message, message_detail)

        if ex:
            message = "%s - %s" % (message, ex.message)

        Exception.__init__(self, message)


class CLICrawlArgs(list):
    """During spider creation, spiders are run from the command line
    using the standard Python if __name__ == "__main__". In this mode,
    arguments to the spider's crawl function will come from the
    command line and extracted by interogating sys.argv - again, just
    like a standard Python app. If no command line arguments are
    available but the spider requires crawl args it would be great
    if the spider prompted the user to enter each of the crawl args.
    Of course the spider should be careful when it comes to
    prompting for authenticating factors (passwords etc) not to echo
    back the characters as they are entered. Further, given the
    spider's metadata declares how to validate crawl arguments, as
    the crawl args are entered by the user, the spider should validate
    the entered text against the spider's metadata. There are other
    scenarios to consider too. What if 2 sys.argv values are given
    but the spider requires 4? Simplest thing would be to display
    a usage message.

    So what does CLICrawlArgs do? Everything described above! The
    last few statements in a spider should look like the code below
    and everything described above is done by CLICrawlArgs:

        if __name__ == "__main__"
            crawl_args = cloudfeaster.spider.CLICrawlArgs(MySpider)
            crawl_result = MySpider.walk(*crawl_args)
            print json.dumps(crawl_result, indent=4)

    CLICrawlArgs depends heavily on a spider's metadata so spend
    the time to get the metadata right.
    """

    def __init__(self, spider_class):
        list.__init__(self)

        validated_metadata = spider_class.get_validated_metadata()
        factor_display_order = validated_metadata["factor_display_order"]

        if len(factor_display_order) == (len(sys.argv) - 1):
            self.extend(sys.argv[1:])
            return

        # specified some crawl args but we know it isn't the right number
        # of arguments so construct and display a usage message
        if 1 < len(sys.argv):
            usage = "usage: %s" % os.path.split(sys.argv[0])[1]
            for factor in factor_display_order:
                usage = "%s <%s>" % (usage, factor)
            print usage
            # sys.exit() only returns when it's mocked
            sys.exit(1)
            return

        identifying_factors = validated_metadata.get("identifying_factors", {})
        for factor in factor_display_order:
            prompt = "%s: " % factor
            sys.stdout.write(prompt)
            if factor in identifying_factors:
                arg = sys.stdin.readline().strip()
            else:
                arg = getpass.getpass("")
            self.append(arg)


class CrawlResponse(dict):
    """Instances of this class are returned by :py:meth:`Spider.crawl` and
    :py:meth:`Spider.walk`.
    """

    SC_OK = 0
    SC_CRAWL_RAISED_EXCEPTION = 400 + 1
    SC_SPIDER_NOT_FOUND = 400 + 2
    SC_CTR_RAISED_EXCEPTION = 400 + 3
    SC_INVALID_CRAWL_RETURN_TYPE = 400 + 4
    SC_INVALID_CRAWL_ARG = 400 + 6
    SC_BAD_CREDENTIALS = 400 + 7
    SC_ACCOUNT_LOCKED_OUT = 400 + 8
    SC_COULD_NOT_CONFIRM_LOGIN_STATUS = 400 + 9

    def __getattr__(self, name):
        return self.get(name, None)


class CrawlResponseOk(CrawlResponse):

    def __init__(self, data=None):
        CrawlResponse.__init__(
            self,
            status_code=CrawlResponse.SC_OK,
            status="Ok")
        if data is not None:
            self["data"] = data


class CrawlResponseCtrRaisedException(CrawlResponse):

    def __init__(self, ex):
        status = "Spider's ctr raised exception = %s" % ex
        CrawlResponse.__init__(
            self,
            status_code=CrawlResponse.SC_CTR_RAISED_EXCEPTION,
            status=status)


class CrawlResponseSpiderNotFound(CrawlResponse):

    def __init__(self, spider_name):
        status = "Could not find spider '%s'" % spider_name
        CrawlResponse.__init__(
            self,
            status_code=CrawlResponse.SC_SPIDER_NOT_FOUND,
            status=status)


class CrawlResponseCrawlRaisedException(CrawlResponse):

    def __init__(self, ex):
        status = "Spider's crawl raised exception = %s" % ex
        CrawlResponse.__init__(
            self,
            status_code=CrawlResponse.SC_CRAWL_RAISED_EXCEPTION,
            status=status)


class CrawlResponseInvalidCrawlReturnType(CrawlResponse):

    def __init__(self, crawl_response):
        status_fmt = (
            "Spider's crawl returned invalid type '%s' - "
            "expected '%s'"
        )
        status = status_fmt % (type(crawl_response), CrawlResponse)
        CrawlResponse.__init__(
            self,
            status_code=CrawlResponse.SC_INVALID_CRAWL_RETURN_TYPE,
            status=status)


class CrawlResponseInvalidCrawlArg(CrawlResponse):

    def __init__(self, spider, arg_name, arg_value):
        status_fmt = (
            "Spider '%s' crawl arg '%s' has a value of '%s' "
            "which isn't valid - check the spider's metadata"
        )
        status = status_fmt % (spider, arg_name, arg_value)
        CrawlResponse.__init__(
            self,
            status_code=CrawlResponse.SC_INVALID_CRAWL_ARG,
            status=status)


class CrawlResponseBadCredentials(CrawlResponse):

    def __init__(self):
        CrawlResponse.__init__(
            self,
            status_code=CrawlResponse.SC_BAD_CREDENTIALS,
            status="bad credentials")


class CrawlResponseAccountLockedOut(CrawlResponse):

    def __init__(self):
        CrawlResponse.__init__(
            self,
            status_code=CrawlResponse.SC_ACCOUNT_LOCKED_OUT,
            status="account locked out")


class CrawlResponseCouldNotConfirmLoginStatus(CrawlResponse):

    def __init__(self):
        CrawlResponse.__init__(
            self,
            status_code=CrawlResponse.SC_COULD_NOT_CONFIRM_LOGIN_STATUS,
            status="could not confirm login status")
