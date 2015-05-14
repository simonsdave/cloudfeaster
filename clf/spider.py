"""This module defines the core CLF spidering API.
For example, a spider author creates a spider by
creating a new class which derives from :py:class:`Spider`.
Next the spider author implements a :py:meth:`Spider.crawl`
which returns an instance of :py:class:`CrawlResponse`.
Both :py:class:`Spider` and :py:class:`CrawlResponse`
are defined in this module."""

import getpass
import hashlib
import inspect
import logging
import os
import re
import sets
import sys

import jsonschema

_logger = logging.getLogger("CLF_%s" % __name__)

"""Used to simplify the definition of :py:attr:`Spider._metadata_json_schema`
and should only be used in this definition."""
_metadata_factors_pattern_properties = {
    "patternProperties": {
        "^[A-Za-z0-9_\-]+$": {
            "type": "object",
            "oneOf": [
                {"$ref": "#/definitions/pattern"},
                {"$ref": "#/definitions/enum"},
            ],
        },
    },
}

"""Used to simplify the definition of :py:attr:`Spider._metadata_json_schema`
and should only be used in this definition."""
_metadata_pattern_definition = {
    "type": "object",
    "properties": {
        "pattern": {
            "type": "string",
            "minLength": 1,
        },
    },
    "required": [
        "pattern",
    ],
    "additionalProperties": False,
}

"""Used to simplify the definition of :py:attr:`Spider._metadata_json_schema`
and should only be used in this definition."""
_metadata_enum_definition = {
    "type": "object",
    "properties": {
        "enum": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string",
            },
            "uniqueItems": True
        },
    },
    "required": [
        "enum",
    ],
    "additionalProperties": False,
}


class Spider(object):
    """Abstract base class for all spiders"""

    """Used to validate return value of ```metadata()```."""
    _metadata_json_schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "id": "http://api.cloudfeaster.com/v1.00/spider_metadata",
        "title": "Spider Metadata",
        "description": "Spider Metadata",
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "pattern": "^http.+$",
            },
            "ttl": {
                "type": "string",
                "pattern": "\d+[dhms]",
            },
            "max_concurrency": {
                "type": "integer",
                "minimum": 1,
            },
            "identifying_factors": _metadata_factors_pattern_properties,
            "authenticating_factors": _metadata_factors_pattern_properties,
            "factors": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "string",
                    "minLength": 1,
                },
                "uniqueItems": True
            },
        },
        "required": [
            "url",
        ],
        "additionalProperties": False,
        "definitions": {
            "pattern": _metadata_pattern_definition,
            "enum": _metadata_enum_definition,
        },
        # :TODO: what about crawl return values?
        # :TODO: what about vertical specific, community defined descriptions
        # of a site? ex. for loyalty programs should declare something to do
        # with the member's tier status
    }

    @classmethod
    def _get_crawl_method_arg_names(cls):
        """Returns the list of argument names for
        :py:meth:`Spider.crawl`. If the spider doesn't
        have a crawl method return None."""
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
    def get_metadata(cls):
        """Spiders supply their metadata by overriding
        :py:meth:`Spider.get_metadata_definition` and
        those wishing to retrieve a spider's metadata
        should call this method. This method validates
        and potentially modifies the metadata returned
        by :py:meth:`Spider.get_metadata_definition`
        to add aspects of the metadata which can be
        determined by inspecting the spider's source code."""
        rv = cls.get_metadata_definition()

        try:
            jsonschema.validate(rv, cls._metadata_json_schema)
        except Exception as ex:
            raise SpiderMetadataError(cls, ex=ex)

        crawl_method_arg_names = cls._get_crawl_method_arg_names()
        if crawl_method_arg_names is None:
            raise SpiderMetadataError(cls, message_detail="crawl() not found")
        crawl_method_arg_names_as_set = sets.Set(crawl_method_arg_names)

        identifying_factors = rv.get("identifying_factors", {})
        authenticating_factors = rv.get("authenticating_factors", {})
        factor_names = []
        factor_names.extend(identifying_factors.keys())
        factor_names.extend(authenticating_factors.keys())
        if sets.Set(factor_names) != crawl_method_arg_names_as_set:
            message_detail = "crawl() arg names and factor names don't match"
            raise SpiderMetadataError(cls, message_detail=message_detail)

        if "factors" not in rv:
            rv["factors"] = crawl_method_arg_names
        else:
            if sets.Set(rv["factors"]) != crawl_method_arg_names_as_set:
                message_detail = (
                    "crawl() arg names and "
                    "explicit factor names don't match"
                )
                raise SpiderMetadataError(cls, message_detail=message_detail)

        if "ttl" in rv:
            reg_ex_pattern = "(?P<value>\d+)(?P<unit>[dhms])"
            reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
            match = reg_ex.match(rv["ttl"])
            assert match
            value = int(match.group("value"))
            unit = match.group("unit")
            multipliers = {
                "d": 24 * 60 * 60,
                "h": 60 * 60,
                "m": 60,
                "s": 1,
            }
            rv["ttl"] = value * multipliers[unit.lower()]
        else:
            rv["ttl"] = 0

        return rv

    @classmethod
    def get_metadata_definition(cls):
        """Spider classes should override this method to return
        a dict represention of a JSON document which describes the
        spider.

        The minimal would return a dict with ...

        See the sample spiders for a broad variety of metadata
        examples."""
        fmt = "%s must implememt class method metadata()"
        raise NotImplementedError(fmt % cls)

    @property
    def url(self):
        """The URL that the spider will crawl.
        The url is extracted from the spider's metadata.
        If :py:meth:`Spider.get_metadata_definition` is not implemented
        a :py:class:`NotImplementedError` will be
        raised when the property is accessed."""
        cls = type(self)
        metadata = cls.get_metadata()
        return metadata.get("url", None)

    @classmethod
    def version(cls):
        """This method returns a spider's version which is  the SHA1 of
        the source code of the module containing the spider."""
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
        :raises Exception: this method may raises exceptions"""
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
        :rtype: :py:class:`CrawlResponse`"""

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
    """Raised by :py:meth:`Spider.get_metadata` to indicate
    that :py:meth:`Spider.get_metadata_definition` returned
    invalid metadata."""

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
    like a standard Python app. If not command line arguments are
    available but the spider requires crawl args it would be great
    if the spider prompted to user to enter each of the crawl args.
    Of course the spider should be careful when it comes to
    prompting for authenticating factors (passwords etc) not to echo
    back the characters as they are entered. Further, given the
    spider's metadata declares how to validate crawl arguments, as
    the crawl args are entered by the user, the spider should validate
    the entered text against the spider's metadata. There are other
    scenarios to consider to, what if 2 sys.argv values are given
    but the spider requires 4? Simplest thing would be to display
    a usage message.

    So what does CLICrawlArgs do? Everything described above! The
    last few statements in a spider should look like the code below
    and everything described above is done by CLICrawlArgs:

        if __name__ == "__main__"
            crawl_args = clf.spider.CLICrawlArgs(MySpider)
            crawl_result = MySpider.walk(*crawl_args)
            print json.dumps(crawl_result, indent=4)

    CLICrawlArgs depends heavily on a spider's metadata so spend
    the time to get the metadata right.
    """

    def __init__(self, spider_class):
        list.__init__(self)

        metadata = spider_class.get_metadata()
        identifying_factors = metadata.get("identifying_factors", {})
        factor_names = metadata.get("factors", [])

        if len(factor_names) == (len(sys.argv) - 1):
            self.extend(sys.argv[1:])
            return

        if 1 < len(sys.argv):
            usage = "usage: %s" % os.path.split(sys.argv[0])[1]
            for factor_name in factor_names:
                usage = "%s <%s>" % (usage, factor_name)
            print usage
            sys.exit(1)
            # sys.exit() only returns when it's mocked
            return

        for factor_name in factor_names:
            prompt = "%s: " % factor_name
            sys.stdout.write(prompt)
            if factor_name in identifying_factors:
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
