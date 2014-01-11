"""This module declares :py:class:`Spider` which is an abstract base class
from which all spider classes are derived. In addition,
:py:class:`CrawlResponse` is declared."""

import hashlib
import inspect
import logging
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
            # :TODO: really a min length of 1?
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
                "pattern": "^http.+$"
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

    def walk(self, *args):
        """This method is intended for use by the CLF infrastructure.
        Spiders should not use this method. Always returns a
        :py:class:`CrawlResponse` and won't throw an exception."""

        rv = None
        try:
            rv = self.crawl(*args)
            if not isinstance(rv, CrawlResponse):
                status_fmt = "Invalid crawl return type '%s'. Expected '%s'"
                rv = CrawlResponse(
                    CrawlResponse.SC_INVALID_CRAWL_RETURN_TYPE,
                    status=status_fmt % (type(rv), CrawlResponse)
                )
        except Exception as ex:
            rv = CrawlResponse(
                CrawlResponse.SC_CRAWL_THREW_EXCEPTION,
                status=str(ex))

        return rv

    def crawl(self, *args):
        """Spiders should override this method to implement
        their own crawling logic.

        :param args: arguments to the crawl method - typically credentials
        :return: result of the crawl
        :rtype: :py:class:`CrawlResponse`"""
        fmt = "%s must implememt crawl()"
        raise NotImplementedError(fmt % self)


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


class CrawlResponse(dict):
    """Instances of this class are returned by :py:meth:`Spider.crawl` and
    :py:meth:`Spider.walk`."""

    SC_OK = 0
    SC_WALK_THREW_EXCEPTION = 400 + 1
    SC_CRAWL_THREW_EXCEPTION = SC_WALK_THREW_EXCEPTION
    SC_SPIDER_NOT_FOUND = 400 + 2
    SC_SPIDER_CTR_THREW_EXCEPTION = 400 + 3
    SC_INVALID_CRAWL_RETURN_TYPE = 400 + 4
    SC_INVALID_CRAWL_ARG = 400 + 6
    SC_BAD_CREDENTIALS = 400 + 7
    SC_ACCOUNT_LOCKED_OUT = 400 + 8
    SC_COULD_NOT_CONFIRM_LOGIN_STATUS = 400 + 9

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
