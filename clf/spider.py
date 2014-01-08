"""This module declares :py:class:`Spider` which is an abstract base class
from which all spider classes are derived. In addition,
:py:class:`CrawlResponse` is declared."""

import hashlib
import inspect
import logging
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
            "items": {"type": "string"},
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
    def metadata(cls):
        """Spider classes should override this method to return
        a dict represention of a JSON document which describes the
        spider.

        The minimal would return a dict with ...

        See the sample spiders for a broad variety of metadata
        examples."""
        fmt = "%s must implememt class method metadata()"
        raise NotImplementedError(fmt % cls)

    @classmethod
    def is_metadata_ok(cls):
        """Use ```_metadata_json_schema``` to validate
        the return value of ```metadata()```. Returns
        ```True``` if the validation is successful otherwise
        return ```False```."""
        try:
            jsonschema.validate(cls.metadata(), cls._metadata_json_schema)
        except Exception as ex:
            _logger.error(str(ex))
            return False
        return True

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
            if type(rv) != CrawlResponse:
                status_fmt = "Invalid crawl return type '%s'. Expected '%s'"
                rv = CrawlResponse(
                    CrawlResponse.SC_INVALID_CRAWL_RETURN_TYPE,
                    status=status_fmt % (type(rv), CrawlResponse)
                )
        except Exception as ex:
            rv = CrawlResponse(CrawlResponse.SC_CRAWL_THREW_EXCEPTION, status=str(ex))

        return rv

    def crawl(self, *args):
        """Spiders should override this method to implement
        their own crawling logic.

        :param args: arguments to the crawl method - typically credentials
        :return: result of the crawl
        :rtype: :py:class:`CrawlResponse`"""

        rv = CrawlResponse(
            CrawlResponse.SC_CRAWL_NOT_IMPLEMENTED,
            status="'%s' didn't implement crawl()" % type(self).__name__
        )
        return rv


class CrawlResponse(dict):
    """Instances of this class are returned by :py:meth:`Spider.crawl` and
    :py:meth:`Spider.walk`."""

    SC_OK = 0
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
