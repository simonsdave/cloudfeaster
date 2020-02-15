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
import logging
import logging.config
import os
import pkg_resources
import pkgutil
import re
import sys
import time
import tempfile

import colorama
import dateutil.parser
import jsonschema
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.chrome.options import Options
import selenium.webdriver.support.select

import cloudfeaster_extension
from . import jsonschemas
from . import privacy

_logger = logging.getLogger(__name__)

# making calls to time.sleep() easier to understand
_quarter_of_a_second = 0.25

# making calls to time.sleep() easier to understand
_half_a_second = 0.5

# making calls to time.sleep() easier to understand
_one_second = 1


def _snake_to_camel_case(s):
    return re.sub(
        '_(.)',
        lambda match: match.group(1).upper(),
        s)


def _utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())


class Spider(object):
    """Base class for all spiders"""

    @classmethod
    def _get_crawl_method_arg_names_for_use_as_factors(cls):
        """Returns the list of argument names for
        crawl(). If the spider doesn't have a crawl method
        returns None.
        """
        def is_crawl_instance_method(t):
            if not inspect.isfunction(t):
                return False

            # if inspect.isclass(t.__self__):
            #     return False

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
            # 2: below since all crawl methods should have @ least 2 args
            # arg 1 = self ie. the spider instance
            # arg 2 = browser
            return inspect.getfullargspec(t).args[2:]

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
            jsonschema.validate(metadata, jsonschemas.spider_metadata)
        except Exception as ex:
            raise SpiderMetadataError(cls, ex=ex)

        crawl_method_arg_names = cls._get_crawl_method_arg_names_for_use_as_factors()
        if crawl_method_arg_names is None:
            message_detail = "crawl() method arg names not found"
            raise SpiderMetadataError(cls, message_detail=message_detail)

        identifying_factors = metadata.get("identifyingFactors", {})
        metadata["identifyingFactors"] = identifying_factors

        authenticating_factors = metadata.get("authenticatingFactors", {})
        metadata["authenticatingFactors"] = authenticating_factors

        factors = list(identifying_factors.keys())
        factors.extend(authenticating_factors.keys())

        camel_cased_factors = [_snake_to_camel_case(factor) for factor in factors]
        expected_camel_cased_crawl_method_arg_names = camel_cased_factors[:]

        camel_cased_crawl_method_arg_names = [_snake_to_camel_case(arg) for arg in crawl_method_arg_names]
        # :QUESTION: why is a `set()` being used here?
        if set(expected_camel_cased_crawl_method_arg_names) != set(camel_cased_crawl_method_arg_names):
            message_detail = "crawl() arg names and factor names don't match"
            raise SpiderMetadataError(cls, message_detail=message_detail)

        #
        # factor display order ...
        #

        factor_display_order = metadata.get("factorDisplayOrder", None)
        if factor_display_order is None:
            metadata["factorDisplayOrder"] = camel_cased_crawl_method_arg_names
        else:
            if set(factors) != set(factor_display_order):
                message_detail = "factors and factor display order don't match"
                raise SpiderMetadataError(cls, message_detail=message_detail)

        #
        # factor display names ...
        #

        # can only have factor display names for previously identified
        # identifying and authenticating factors
        factor_display_names = metadata.get("factorDisplayNames", {})
        if not set(factor_display_names).issubset(set(factors)):
            message_detail = "unknown factor(s) in factor display names"
            raise SpiderMetadataError(cls, message_detail=message_detail)

        # ensure each factor has a factor display name available for
        # the default language
        for factor_name in factors:
            lang_to_display_name = factor_display_names.get(factor_name, {})
            if "" not in lang_to_display_name:
                lang_to_display_name[""] = factor_name
            factor_display_names[factor_name] = lang_to_display_name
        metadata["factorDisplayNames"] = factor_display_names

        #
        # TTL
        #
        metadata["ttl"] = metadata.get("ttl", "60s")

        #
        # max concurrent crawls
        #
        metadata["maxConcurrentCrawls"] = metadata.get("maxConcurrentCrawls", 3)

        #
        # parnoia level
        #
        metadata["paranoiaLevel"] = metadata.get("paranoiaLevel", "low")

        #
        # maximum crawl time
        #
        metadata["maxCrawlTime"] = metadata.get("maxCrawlTime", "30s")

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

    @property
    def paranoia_level(self):
        """Returns the spider's paranoia level."""
        metadata = type(self).get_validated_metadata()
        return metadata["paranoiaLevel"]

    @classmethod
    def version(cls):
        """This method returns a spider's version which is  the SHA1 of
        the source code of the module containing the spider.
        """
        module = sys.modules[cls.__module__]
        source = inspect.getsource(module)
        hash = hashlib.sha256(source.encode('UTF-8'))
        return '%s:%s' % (hash.name, hash.hexdigest())

    def crawl(self, browser, *args, **kwargs):
        """Spiders should override this method to implement
        their own crawling logic.
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
            message = "%s - %s" % (message, str(ex))

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

        from cloudfeaster import spider

        .
        .
        .

        if __name__ == '__main__':
            crawl_args = spider.CLICrawlArgs(MySpider)
            crawler = spider.SpiderCrawler(PyPISpider)
            crawl_result = crawler.crawl(*crawl_args)
            print(json.dumps(crawl_result))
            sys.exit(1 if crawl_result.status_code else 0)

    CLICrawlArgs depends heavily on a spider's metadata so spend
    the time to get the metadata right.
    """

    def __init__(self, spider_class):
        list.__init__(self)

        validated_metadata = spider_class.get_validated_metadata()
        factor_display_order = validated_metadata["factorDisplayOrder"]
        factor_display_names = validated_metadata["factorDisplayNames"]
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
            print(usage)
            # sys.exit() only returns when it's mocked
            sys.exit(1)
            return

        identifying_factors = validated_metadata.get("identifyingFactors", {})
        authenticating_factors = validated_metadata.get("authenticatingFactors", {})
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
    """Instances of this class are returned by ```Spider.crawl```."""

    SC_OK = 0
    SC_CRAWL_RAISED_EXCEPTION = 400 + 1
    SC_SPIDER_NOT_FOUND = 400 + 2
    SC_CTR_RAISED_EXCEPTION = 400 + 3
    SC_INVALID_CRAWL_RETURN_TYPE = 400 + 4
    SC_INVALID_CRAWL_RESPONSE = 400 + 5
    SC_INVALID_CRAWL_ARG = 400 + 6
    SC_BAD_CREDENTIALS = 400 + 7
    SC_ACCOUNT_LOCKED_OUT = 400 + 8
    SC_COULD_NOT_CONFIRM_LOGIN_STATUS = 400 + 9
    SC_UNKNOWN = 500

    def __init__(self, status_code, status, *args, **kwargs):
        kwargs['_metadata'] = {
            'status': {
                'code': status_code,
                'message': status,
            },
        }
        dict.__init__(self, *args, **kwargs)

    def add_debug(self, key, value):
        if '_debug' not in self:
            self['_debug'] = {}

        self['_debug'][key] = value

    @property
    def status_code(self):
        return self.get('_metadata', {}).get('status', {}).get('code', type(self).SC_UNKNOWN)


class CrawlResponseOk(CrawlResponse):

    def __init__(self, *args, **kwargs):
        CrawlResponse.__init__(self,
                               CrawlResponse.SC_OK,
                               'Ok',
                               *args, **kwargs)


class CrawlResponseBadCredentials(CrawlResponse):

    def __init__(self, *args, **kwargs):
        CrawlResponse.__init__(self,
                               CrawlResponse.SC_BAD_CREDENTIALS,
                               'bad credentials',
                               *args,
                               **kwargs)


class CrawlResponseAccountLockedOut(CrawlResponse):

    def __init__(self, *args, **kwargs):
        CrawlResponse.__init__(self,
                               CrawlResponse.SC_ACCOUNT_LOCKED_OUT,
                               'account locked out',
                               *args,
                               **kwargs)


class CrawlResponseCouldNotConfirmLoginStatus(CrawlResponse):

    def __init__(self, *args, **kwargs):
        CrawlResponse.__init__(self,
                               CrawlResponse.SC_COULD_NOT_CONFIRM_LOGIN_STATUS,
                               'could not confirm login status',
                               *args,
                               **kwargs)


class CrawlResponseInvalidCrawlReturnType(CrawlResponse):

    def __init__(self, *args, **kwargs):
        CrawlResponse.__init__(self,
                               CrawlResponse.SC_INVALID_CRAWL_RETURN_TYPE,
                               'spider crawl returned invalid type',
                               *args,
                               **kwargs)


class CrawlResponseInvalidCrawlResponse(CrawlResponse):
    def __init__(self, ex, *args, **kwargs):
        CrawlResponse.__init__(self,
                               CrawlResponse.SC_INVALID_CRAWL_RESPONSE,
                               'spider crawl returned invalid response - %s' % ex,
                               *args,
                               **kwargs)


class CrawlResponseCrawlRaisedException(CrawlResponse):

    def __init__(self, ex, *args, **kwargs):
        CrawlResponse.__init__(self,
                               CrawlResponse.SC_CRAWL_RAISED_EXCEPTION,
                               'spider crawl raised exception - %s' % ex,
                               *args,
                               **kwargs)


class CrawlResponseCtrRaisedException(CrawlResponse):

    def __init__(self, ex, *args, **kwargs):
        CrawlResponse.__init__(self,
                               CrawlResponse.SC_CTR_RAISED_EXCEPTION,
                               'spider ctr raised exception - %s' % ex,
                               *args,
                               **kwargs)


class CrawlResponseSpiderNotFound(CrawlResponse):

    def __init__(self, full_spider_class_name, *args, **kwargs):
        CrawlResponse.__init__(self,
                               CrawlResponse.SC_SPIDER_NOT_FOUND,
                               'could not find spider %s' % full_spider_class_name,
                               *args,
                               **kwargs)


class SpiderCrawler(object):
    """SpiderCrawler is a wrapper for ```Spider.crawl()``` ensuring
    exceptions are always caught and and instance of ```CrawlResponse```
    are always returned.

    Below is the expected spider mainline illustrating how ```SpiderCrawler```
    is expected to be used.

        if __name__ == '__main__':
            crawl_args = spider.CLICrawlArgs(PyPISpider)
            crawler = spider.SpiderCrawler(PyPISpider)
            crawl_result = crawler.crawl(crawl_args)
            print(json.dumps(crawl_result))
            sys.exit(1 if crawl_result.status_code else 0)
    """

    def __init__(self, full_spider_class_name):
        object.__init__(self)

        self.full_spider_class_name = full_spider_class_name

        self.logging_file = None
        self.chromedriver_log_file = None
        self.screenshot_file = None

    def crawl(self, *args, **kwargs):
        self._configure_logging(args)

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
            spider = spider_class()
        except Exception as ex:
            return CrawlResponseCtrRaisedException(ex)

        #
        # call the spider's crawl() method, validate crawl
        # response and add crawl response metadata
        #
        dt_start = _utc_now()
        try:
            (_, self.chromedriver_log_file) = tempfile.mkstemp()
            with self._get_browser(spider.url, spider.paranoia_level, self.chromedriver_log_file) as browser:
                try:
                    crawl_response = spider.crawl(browser, *args, **kwargs)
                except Exception as ex:
                    crawl_response = CrawlResponseCrawlRaisedException(ex)

                if not isinstance(crawl_response, CrawlResponse):
                    crawl_response = CrawlResponseInvalidCrawlReturnType()

                crawl_response = self._take_screenshot(browser, crawl_response)
        except Exception as ex:
            crawl_response = CrawlResponseCrawlRaisedException(ex)
        dt_end = _utc_now()

        crawl_response['_metadata'].update({
            'spider': {
                'name': '%s.%s' % (type(spider).__module__, type(spider).__name__),
                'version': spider_class.version(),
            },
            'crawlArgs': [
            ],
            'crawlTime': {
                'started': dt_start.isoformat(),
                'durationInMs': int(1000.0 * (dt_end - dt_start).total_seconds()),
            },
        })

        if self.logging_file:
            crawl_response.add_debug('crawlLog', self.logging_file)

        if self.chromedriver_log_file:
            crawl_response.add_debug('chromeDriverLog', self.chromedriver_log_file)

        for arg in args:
            crawl_response['_metadata']['crawlArgs'].append(privacy.hash_crawl_arg(arg))

        #
        # verify ```crawl_response```
        #
        try:
            jsonschema.validate(crawl_response, jsonschemas.crawl_result)
        except Exception as ex:
            return CrawlResponseInvalidCrawlResponse(ex)

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
                return (None, CrawlResponseSpiderNotFound(self.full_spider_class_name))

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
            return (None, CrawlResponseSpiderNotFound(self.full_spider_class_name))

    def _get_browser(self, url, paranoia_level, chromedriver_log_file):
        """This private method exists to allow unit tests to mock out the method.
        export CLF_REMOTE_CHROMEDRIVER=http://host.docker.internal:9515
        """
        remote_chromedriver = os.environ.get('CLF_REMOTE_CHROMEDRIVER', None)
        if remote_chromedriver:
            return RemoteBrowser(remote_chromedriver, url, paranoia_level)
        return Browser(url, paranoia_level, chromedriver_log_file)

    def _take_screenshot(self, browser, crawl_response):
        """This is a private method which takes a screenshot of the browser's
        current window and then adds the name of the temp file containing the
        screenshot to the crawl response.
        """
        (_, no_extension_screenshot) = tempfile.mkstemp()
        self.screenshot_file = no_extension_screenshot + '.png'
        os.rename(no_extension_screenshot, self.screenshot_file)
        browser.save_screenshot(self.screenshot_file)
        crawl_response.add_debug('screenshot', self.screenshot_file)
        return crawl_response

    def _configure_logging(self, crawl_args):
        clf_debug_value = os.environ.get('CLF_DEBUG', '')
        reg_ex_pattern = '^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$'
        reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
        logging_level = clf_debug_value.upper() if reg_ex.match(clf_debug_value) else 'ERROR'

        (_, self.logging_file) = tempfile.mkstemp()

        logging.Formatter.converter = time.gmtime

        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s.%(msecs)03d+00:00 %(levelname)s %(module)s:%(lineno)d %(message)s',
                },
            },
            'handlers': {
                'file': {
                    'class': 'logging.FileHandler',
                    'filename': self.logging_file,
                    'mode': 'a',
                    'formatter': 'standard',
                    'filters': [
                        # privacy.RedactingFilter(crawl_args),
                    ],
                },
            },
            'root': {
                'level': logging_level,
                'handlers': [
                    'file',
                ],
            },
        }

        logging.config.dictConfig(logging_config)

        # :TODO: can this be configured in 'logging_config'?
        # privacy.RedactingFormatter.install_for_all_handlers(crawl_args)


class RemoteBrowser(webdriver.Remote):

    def __init__(self, remote_chromedriver, url, paranoia_level):
        webdriver.Remote.__init__(self, remote_chromedriver)

        self._url = url
        self._paranoia_level = paranoia_level

    def __enter__(self):
        """Along with ```___exit___()``` implements the standard
        context manager pattern which, if a none-None url was
        supplied in the ```Browser```'s ctr,
        directs the browser to the specified url when entering
        the context and closes the browser when exiting the
        context. The pattern just makes using
        ```Browser``` way, way cleaner.
        """
        if self._url:
            self.get(self._url)
        return self

    def __exit__(self, exec_type, exec_val, ex_tb):
        """See ```___enter___()```."""
        self.quit()

    def create_web_element(self, element_id):
        """Override the default implementation of
        ```webdriver.Chrome.create_web_element```
        to return a ```WebElement``` instead of a
        ```selenium.webdriver.remote.webelement.WebElement```.
        """
        return WebElement(self._paranoia_level, self, element_id)


class Browser(webdriver.Chrome):
    """This class extends ```webdriver.Chrome``` to add new functionality
    and override existing functionality that is well suited to writing
    webdriver based Spiders.
    """

    @classmethod
    def get_chrome_options(cls, paranoia_level):
        chrome_options = Options()

        binary_location = os.environ.get('CLF_CHROME', None)
        if binary_location:
            chrome_options.binary_location = binary_location
            _logger.info('using chrome binary >>>%s<<<', chrome_options.binary_location)

        # re '--no-sandbox' - see https://github.com/theintern/intern/issues/878
        chrome_options_str = os.environ.get(
            'CLF_CHROME_OPTIONS',
            '--headless|--window-size=1280x1024|--no-sandbox|--user-agent=%s' % cloudfeaster_extension.user_agent())
        for chrome_option in chrome_options_str.split('|'):
            chrome_options.add_argument(chrome_option)
            _logger.info('using chrome option >>>%s<<<', chrome_option)

        (proxy_host, proxy_port) = cloudfeaster_extension.proxy(paranoia_level)
        if proxy_host is not None and proxy_port is not None:
            chrome_option = '--proxy-server=%s:%d' % (proxy_host, proxy_port)
            chrome_options.add_argument(chrome_option)
            _logger.info('using chrome option >>>%s<<<', chrome_option)

        return chrome_options

    def __init__(self, url, paranoia_level, chromedriver_log_file):
        """Create a new instance of :py:class:`Browser`.

        See :py:meth:`Browser.___enter___` to understand how and when the
        ```url``` argument is used.
        """
        chrome_options = type(self).get_chrome_options(paranoia_level)

        service_args = []

        # nice reference @ http://chromedriver.chromium.org/logging
        if chromedriver_log_file:
            _logger.info('chromedriver logs @ >>>%s<<<', chromedriver_log_file)

            service_args.append('--verbose')
            service_args.append('--log-path=%s' % chromedriver_log_file)

        webdriver.Chrome.__init__(
            self,
            chrome_options=chrome_options,
            service_args=service_args)

        self._url = url
        self._paranoia_level = paranoia_level

    def __enter__(self):
        """Along with ```___exit___()``` implements the standard
        context manager pattern which, if a none-None url was
        supplied in the ```Browser```'s ctr,
        directs the browser to the specified url when entering
        the context and closes the browser when exiting the
        context. The pattern just makes using
        ```Browser``` way, way cleaner.
        """
        if self._url:
            self.get(self._url)
        return self

    def __exit__(self, exec_type, exec_val, ex_tb):
        """See ```___enter___()```."""
        self.quit()

    def create_web_element(self, element_id):
        """Override the default implementation of
        ```webdriver.Chrome.create_web_element```
        to return a :py:class:`WebElement` instead of a
        ```selenium.webdriver.remote.webelement.WebElement```.
        """
        return WebElement(self._paranoia_level, self, element_id)

    def wait_for_login_to_complete(self,
                                   ok_xpath_locator,
                                   bad_credentials_xpath_locator=None,
                                   account_locked_out_xpath_locator=None,
                                   alert_displayed_indicates_bad_credentials=False,
                                   number_seconds_until_timeout=30):

        for i in range(0, number_seconds_until_timeout):
            if self._find_element_by_xpath(ok_xpath_locator):
                return None

            if bad_credentials_xpath_locator:
                if self._find_element_by_xpath(bad_credentials_xpath_locator):
                    return CrawlResponseBadCredentials()

            if alert_displayed_indicates_bad_credentials:
                if self._is_alert_dialog_displayed():
                    return CrawlResponseBadCredentials()

            if account_locked_out_xpath_locator:
                if self._find_element_by_xpath(account_locked_out_xpath_locator):
                    return CrawlResponseAccountLockedOut()

            time.sleep(_one_second)

        return CrawlResponseCouldNotConfirmLoginStatus()

    def wait_for_signin_to_complete(self,
                                    ok_xpath_locator,
                                    bad_credentials_xpath_locator=None,
                                    account_locked_out_xpath_locator=None,
                                    alert_displayed_indicates_bad_credentials=None,
                                    number_seconds_until_timeout=30):
        """This method is just another name for
        :py:meth:`wait_for_login_to_complete` so that spider authors
        can use "login" or "signin" terminology to match
        the semantics of the web site being crawled.
        """
        rv = self.wait_for_login_to_complete(
            ok_xpath_locator,
            bad_credentials_xpath_locator,
            account_locked_out_xpath_locator,
            alert_displayed_indicates_bad_credentials,
            number_seconds_until_timeout)
        return rv

    def _find_element_by_xpath(self, xpath_locator):
        try:
            self.find_element_by_xpath(xpath_locator)
        except NoSuchElementException:
            return False
        except UnexpectedAlertPresentException:
            return False

        return True

    def _is_alert_dialog_displayed(self):
        """Only to be used by CLF infrastructure.

        Couldn't find a good way to test if a JavaScript alert
        dialog was displayed and hence the creation of this
        method. A word of warning. Don't like the implementation
        of this method because it calls switch_to_alert() which
        will (surprise, surprise) switch focus to the alert dialog
        if the dialog is displayed which is almost certainly not
        the desired behaviour. Because of this side effect it's
        probably only wise to use this method when precense of
        alert dialog indicates an error and your spider will be
        terminated if the alert is displayed.
        """
        try:
            alert = self.switch_to_alert()
            alert.text
        except NoAlertPresentException:
            return False

        return True


class WebElement(selenium.webdriver.remote.webelement.WebElement):
    """This class extends ```selenium.webdriver.remote.webelement.WebElement```
    to add new functionality and override existing functionality that is well
    suited to writing webdriver based Spiders.
    """

    _nonDigitAndNonDigitRegEx = re.compile(r'[^\d^\.]')

    def __init__(self, paranoia_level, *args, **kwargs):
        selenium.webdriver.remote.webelement.WebElement.__init__(self, *args, **kwargs)

        self._paranoia_level = paranoia_level

    def get_text(self):
        """This method exists so spider code can access element data
        using a set of methods instead of a text property and some
        other methods like ```get_int()``` and ```get_float()```.
        """
        return self.text

    def _get_number(self, number_type, reg_ex):
        text = self.get_text()

        if reg_ex:
            match = reg_ex.match(text)
            if match is None:
                return None
            match_groups = match.groups()
            if 1 != len(match_groups):
                return None
            text = match_groups[0]

        text = type(self)._nonDigitAndNonDigitRegEx.sub('', text)
        return number_type(text)

    def get_int(self, reg_ex=None):
        return self._get_number(int, reg_ex)

    def get_float(self, reg_ex=None):
        return self._get_number(float, reg_ex)

    def get_selected(self):
        """This method is here only to act as a shortcut so that a spider
        author can write a single line of code to get the correctly selected
        option in a list rather than the few lines of code that's seen
        in this method's implementation.

        If an option is selected the option's text is returned otherwise
        None is returned.
        """
        select = selenium.webdriver.support.select.Select(self)
        try:
            return select.first_selected_option
        except NoSuchElementException:
            return None

    def select_by_visible_text(self, visible_text):
        """This method is here only to act as a shortcut so that a spider
        author can write a single line of code to select an option in a list
        rather than two lines of code. Perhaps not a huge saving by every
        little bit helps. As an aside, feels like this is the way the
        select functionality should have been implemented anyway.
        """
        select = selenium.webdriver.support.select.Select(self)
        select.select_by_visible_text(visible_text)

    def send_keys(self, value):
        """:ODD: yes this implementation pattern looks odd. This approach is used
        so there's a default implemenation which can be used during development
        but also provides a clean approach to override the implementation.
        """
        cloudfeaster_extension.send_keys(self._paranoia_level, self, value)


class SpiderDiscovery(object):
    """Discover all available spiders. This means locating concrete derived classes
    of ```Spider``` in all available distributions.
    """

    #
    # egg_name_reg_ex is used to extract module names from egg_names
    # like ```gaming_spiders-0.1.0-py2.7```.
    #
    _egg_name_reg_ex = re.compile(
        r'^\s*(?P<egg_name>.+spiders)-\d+\.\d+\.\d+\-py\d+\.\d+\s*$',
        re.IGNORECASE)

    def discover(self):

        #
        # find and import all packages that might contain spiders
        #
        for distro in pkg_resources.working_set:
            match = type(self)._egg_name_reg_ex.match(distro.egg_name())
            _logger.info("assessing distro for spiders '%s'", distro.egg_name())
            if match:
                egg_name = match.group('egg_name')
                _logger.info("matched distro for spiders '%s'", egg_name)
                type(self).load_and_discover_all_spiders_in_package(egg_name)

        #
        # with all packages loaded that might contain spiders, find all
        # the concrete subclasses of ```cloudfeaster.spider.Spider```
        # which will be the spiders we're interested in
        #
        return self._find_concrete_spider_classes(Spider)

    def _find_concrete_spider_classes(self, base_class):
        base_msg = "looking for concrete spider classes of base class '%s.%s'" % (
            base_class.__module__,
            base_class.__name__,
        )
        _logger.info(base_msg)

        rv = {}
        for sub_class in base_class.__subclasses__():
            full_sub_class_name = '%s.%s' % (sub_class.__module__, sub_class.__name__)

            _logger.info("%s - assessing '%s'", base_msg, full_sub_class_name)

            if not sub_class.__subclasses__():
                _logger.info("%s - identified concrete class '%s'", base_msg, full_sub_class_name)

                rv[full_sub_class_name] = sub_class.get_validated_metadata()
            else:
                _logger.info("%s - identified abstract class '%s'", base_msg, full_sub_class_name)

                rv.update(self._find_concrete_spider_classes(sub_class))

        return rv

    @classmethod
    def load_and_discover_all_spiders_in_package(cls, spider_package_name):
        """This is a public class method mostly because sometimes in testing it's super
        useful to be able to load spider distros.
        """
        spider_package = importlib.import_module(spider_package_name)
        spider_package_dir_name = os.path.dirname(spider_package.__file__)
        _logger.info("looking for spiders in directory '%s'", spider_package_dir_name)
        for (_, name, ispkg) in pkgutil.iter_modules([spider_package_dir_name]):
            if not ispkg:
                module_name = '%s.%s' % (spider_package_name, name)
                _logger.info("attempting to import spider module '%s'", module_name)
                importlib.import_module(module_name)
