"""This module defines the core CLF spidering API.
For example, a spider author creates a spider by
creating a new class which derives from :py:class:`Spider`.
Next the spider author implements a :py:meth:`Spider.crawl`
which returns an instance of :py:class:`CrawlResponse`.
Both :py:class:`Spider` and :py:class:`CrawlResponse`
are defined in this module.
"""

import copy
import datetime
import getpass
import hashlib
import inspect
import imp
import importlib
import json
import logging
import os
import re
import sets
import sys

import colorama
import dateutil.parser
import jsonschema

_logger = logging.getLogger(__name__)


def _utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())


def _load_spider_metadata_jsonschema():
    filename = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'jsonschemas',
        'spider_metadata.json')
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
            # permit a concrete spider (cls) to be
            # derived from an abstract base class
            # spider that's defined in a different
            # module but also make sure somewhere
            # in the inheritence hierarchy that something
            # other than Spider has defined a crawl
            # method
            if t.__module__ == Spider.__module__:
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

        # making a copy of the metadata because we're going to
        # potentially make modifications to the metadata and
        # didn't want to mess with the original
        metadata = copy.deepcopy(cls.get_metadata())

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

        #
        # factor display order ...
        #

        factor_display_order = metadata.get("factor_display_order", None)
        if factor_display_order is None:
            metadata["factor_display_order"] = crawl_method_arg_names
        else:
            if sets.Set(factors) != sets.Set(factor_display_order):
                message_detail = "factors and factor display order don't match"
                raise SpiderMetadataError(cls, message_detail=message_detail)

        #
        # factor display names ...
        #

        # can only have factor display names for previously identified
        # identifying and authenticating factors
        factor_display_names = metadata.get("factor_display_names", {})
        if not sets.Set(factor_display_names).issubset(sets.Set(factors)):
            message_detail = "unknown factor(s) in factor display names"
            raise SpiderMetadataError(cls, message_detail=message_detail)

        # ensure each factor has a factor display name available for
        # the default language
        for factor_name in factors:
            lang_to_display_name = factor_display_names.get(factor_name, {})
            if "" not in lang_to_display_name:
                lang_to_display_name[""] = factor_name
            factor_display_names[factor_name] = lang_to_display_name
        metadata["factor_display_names"] = factor_display_names

        #
        # TTL
        #

        ttl = metadata.get("ttl", 60)
        metadata["ttl"] = ttl

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
        hash = hashlib.sha1(source)
        return '%s:%s' % (hash.name, hash.hexdigest())

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
    """During spider authoring, spiders are run from the command line
    using the standard Python if __name__ == "__main__". In this mode,
    arguments to the spider's crawl function will come from the
    command line and extracted by interogating sys.argv - again, just
    like a standard Python app. If no command line arguments are
    available but the spider requires crawl args it would be great
    if the spider prompted the user to enter each of the crawl args.
    Of course the spider should be careful when it comes to
    prompting for authenticating factors (passwords, etc.) not to echo
    back the characters as they are entered. Further, given the
    spider's metadata declares how to validate crawl arguments, as
    the crawl args are entered by the user, the spider should validate
    the entered text against the spider's metadata. There are other
    scenarios to consider too. What if 2 command line args are given
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
        factor_display_names = validated_metadata["factor_display_names"]
        lang = os.environ.get("LANG", "")[:2]

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
        authenticating_factors = validated_metadata.get("authenticating_factors", {})
        factors = identifying_factors.copy()
        factors.update(authenticating_factors)
        for factor_name in factor_display_order:
            while True:
                arg = self.prompt_for_and_get_arg_value(
                    lang,
                    factor_name,
                    factor_name in identifying_factors,
                    factors,
                    factor_display_names)
                if arg is not None:
                    break
            self.append(arg)

    def prompt_for_and_get_arg_value(self,
                                     lang,
                                     factor_name,
                                     is_identifying_factor,
                                     factors,
                                     factor_display_names):
        """Prompt the user for the arg value for a factor.
        Sounds like a pretty simple process but there is
        complexity in scenarios where factors are enums and
        the entire enum list is presented to the user.
        The arg value is also validated against either the
        factor's regular expression or the enum list.

        If a valid value is entered it is returned otherwise
        None is returned. It is expected that the caller
        is in a tight loop iterating over this method until
        a non-None response is returned for the factor.
        """
        factor_display_name = factor_display_names[factor_name].get(
            lang,
            factor_display_names[factor_name].get("", factor_name))

        enums = factors[factor_name].get("enum", None)

        if enums:
            prompt = "%s\n%s\n> " % (
                factor_display_name,
                "\n".join(["- %d. %s" % (i + 1, enums[i]) for i in range(0, len(enums))]),
                )
        else:
            prompt = "%s%s%s> " % (colorama.Style.BRIGHT, factor_display_name, colorama.Style.RESET_ALL)

        sys.stdout.write(prompt)

        if is_identifying_factor:
            arg = sys.stdin.readline().strip()

            if enums:
                try:
                    arg = int(arg)
                    if 1 <= arg and arg <= len(enums):
                        return enums[int(arg) - 1]
                    return None
                except Exception:
                    return None
        else:
            arg = getpass.getpass("")

        reg_ex_pattern = factors[factor_name]["pattern"]
        reg_ex = re.compile(reg_ex_pattern)
        if not reg_ex.match(arg):
            return None

        return arg


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

    def __init__(self, *args, **kwargs):
        kwargs['_status_code'] = CrawlResponse.SC_OK
        kwargs['_status'] = 'Ok'
        CrawlResponse.__init__(self, *args, **kwargs)


class CrawlResponseBadCredentials(CrawlResponse):

    def __init__(self, *args, **kwargs):
        kwargs['_status_code'] = CrawlResponse.SC_BAD_CREDENTIALS
        kwargs['_status'] = 'bad credentials'
        CrawlResponse.__init__(self, *args, **kwargs)


class CrawlResponseAccountLockedOut(CrawlResponse):

    def __init__(self, *args, **kwargs):
        kwargs['_status_code'] = CrawlResponse.SC_ACCOUNT_LOCKED_OUT
        kwargs['_status'] = 'account locked out'
        CrawlResponse.__init__(self, *args, **kwargs)


class CrawlResponseCouldNotConfirmLoginStatus(CrawlResponse):

    def __init__(self, *args, **kwargs):
        kwargs['_status_code'] = CrawlResponse.SC_COULD_NOT_CONFIRM_LOGIN_STATUS
        kwargs['_status'] = 'could not confirm login status'
        CrawlResponse.__init__(self, *args, **kwargs)


class SpiderCrawler(object):
    """SpiderCrawler is a wrapper Spider.crawl() ensuring exceptions are
    always caught and and instance of CrawlResponse are always returned.
    """

    def __init__(self, full_spider_class_name):
        object.__init__(self)

        self.full_spider_class_name = full_spider_class_name

    def crawl(self, *args, **kwargs):
        #
        # get the spider's class
        #
        (spider_class, crawl_response) = self._get_spider_class()
        if crawl_response:
            return crawl_response

        #
        # create an instance of the spider
        #
        try:
            assert spider_class
            spider = spider_class()
        except Exception as ex:
            status = "Spider's ctr raised exception = %s" % ex
            cr = CrawlResponse(
                _status_code=CrawlResponse.SC_CTR_RAISED_EXCEPTION,
                _status=status)
            return cr

        #
        # call the spider's crawl() method
        #
        try:
            dt_start = _utc_now()
            crawl_response = spider.crawl(*args, **kwargs)
            dt_end = _utc_now()
            crawl_time_in_ms = int(1000.0 * (dt_end - dt_start).total_seconds())

            if not isinstance(crawl_response, CrawlResponse):
                status_fmt = (
                    "Spider's crawl returned invalid type '%s' - "
                    "expected '%s'"
                )
                status = status_fmt % (type(crawl_response), CrawlResponse)
                crawl_response = CrawlResponse(
                    _status_code=CrawlResponse.SC_INVALID_CRAWL_RETURN_TYPE,
                    _status=status)
                return crawl_response

            crawl_response['_spider'] = {
                'name': '%s.%s' % (type(spider).__module__, type(spider).__name__),
                'version': spider_class.version(),
            }
            crawl_response['_crawl_time'] = dt_start.isoformat()
            crawl_response['_crawl_time_in_ms'] = crawl_time_in_ms
            return crawl_response
        except Exception as ex:
            status = "Spider's crawl raised exception - %s" % ex
            crawl_response = CrawlResponse(
                _status_code=CrawlResponse.SC_CRAWL_RAISED_EXCEPTION,
                _status=status)
            return crawl_response

    def _get_spider_class(self):
        #
        # deal with scenario where self.full_spider_class_name
        # is in fact already a spider's class
        #
        if not isinstance(self.full_spider_class_name, str):
            #
            # so self.full_spider_class_name wasn't actually the name
            # of the spider. or more precisely it wasn't a string and
            # therefore we assume it's actually the spider's class
            #
            return (self.full_spider_class_name, None)

        #
        # is self.full_spider_class_name actually a pointer to a
        # spider sitting in some arbitrary file. this is particuarly
        # useful when testing spiderhost.py
        #
        reg_ex_pattern = r'\s*(?P<spider_module_filename>.+.py):(?P<spider_class_name>[^\s]+Spider)\s*$'
        reg_ex = re.compile(reg_ex_pattern, flags=re.IGNORECASE)
        match = reg_ex.match(self.full_spider_class_name)
        if match:
            try:
                spider_module_filename = match.group('spider_module_filename')
                spider_class_name = match.group('spider_class_name')
                spider_module = imp.load_source('doicareaboutthisname', spider_module_filename)
                spider_class = getattr(spider_module, spider_class_name)
                return (spider_class, None)
            except Exception:
                status = "Could not find spider '%s'" % self.full_spider_class_name
                crawl_response = CrawlResponse(
                    _status_code=CrawlResponse.SC_SPIDER_NOT_FOUND,
                    _status=status)
                return (None, crawl_response)

        #
        # parse the full name of the spider, identify & load the
        # module containing the spider and find the spider class
        # in the loaded module
        #
        try:
            split_full_spider_class_name = self.full_spider_class_name.split(".")
            spider_module_name = ".".join(split_full_spider_class_name[:-1])
            spider_class_name = split_full_spider_class_name[-1]
            spider_module = importlib.import_module(spider_module_name)
            spider_class = getattr(spider_module, spider_class_name)
            return (spider_class, None)
        except Exception:
            status = "Could not find spider '%s'" % self.full_spider_class_name
            crawl_response = CrawlResponse(
                _status_code=CrawlResponse.SC_SPIDER_NOT_FOUND,
                _status=status)
            return (None, crawl_response)
