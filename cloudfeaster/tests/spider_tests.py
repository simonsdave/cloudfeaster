"""This module contains unit tests for the ```spider``` module."""

import hashlib
import http.server
import importlib
import inspect
import re
import sys
import threading
import time
import unittest
import uuid

import mock
from nose.plugins.attrib import attr
import selenium

from .. import spider
import cloudfeaster_extension


class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Only reason this class exists is to stop writing of log messages
    to stdout as part of serving up documents.
    """

    def log_message(fmt, *arg):
        """yes this really is meant to be a no-op"""
        pass

    def do_GET(self):
        key = self.path[1:]
        question_mark_index = key.find('?')
        if 0 <= question_mark_index:
            key = key[:question_mark_index]
        html = HTTPServer.html_pages.get(key, '')
        self.send_response(200 if html else 404)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-length', len(html))
        self.end_headers()
        self.wfile.write(html.encode('UTF-8'))


class HTTPServer(threading.Thread):

    html_pages = {}

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        server_address = ('127.0.0.1', 0)
        httpd = http.server.HTTPServer(
            server_address,
            HTTPRequestHandler)
        self.portNumber = httpd.server_port
        httpd.serve_forever()
        # never returns

    def start(self):
        threading.Thread.start(self)
        # give the HTTP server time to start & initialize itself
        while 'portNumber' not in self.__dict__:
            time.sleep(1)


class TestCrawlResponse(unittest.TestCase):

    def assertCoreResponse(self, cr, status_code):
        self.assertEqual(cr.status_code, status_code)

    def test_ok_no_data(self):
        cr = spider.CrawlResponseOk()
        self.assertCoreResponse(cr, spider.CrawlResponse.SC_OK)

    def test_ok_with_data(self):
        data = {1: 2, 3: 4}
        cr = spider.CrawlResponseOk(data)
        self.assertCoreResponse(cr, spider.CrawlResponse.SC_OK)
        del cr['_metadata']
        self.assertEqual(data, cr)

    def test_bad_credentials(self):
        cr = spider.CrawlResponseBadCredentials()
        self.assertCoreResponse(
            cr,
            spider.CrawlResponse.SC_BAD_CREDENTIALS)

    def test_account_locked_out(self):
        cr = spider.CrawlResponseAccountLockedOut()
        self.assertCoreResponse(
            cr,
            spider.CrawlResponse.SC_ACCOUNT_LOCKED_OUT)

    def test_could_not_confirm_login_status(self):
        cr = spider.CrawlResponseCouldNotConfirmLoginStatus()
        self.assertCoreResponse(
            cr,
            spider.CrawlResponse.SC_COULD_NOT_CONFIRM_LOGIN_STATUS)

    def test_crawl_response_invalid_crawl_return_type(self):
        cr = spider.CrawlResponseInvalidCrawlReturnType()
        self.assertCoreResponse(
            cr,
            spider.CrawlResponse.SC_INVALID_CRAWL_RETURN_TYPE)

    def test_crawl_response_invalid_crawl_response(self):
        ex = Exception()
        cr = spider.CrawlResponseInvalidCrawlResponse(ex)
        self.assertCoreResponse(
            cr,
            spider.CrawlResponse.SC_INVALID_CRAWL_RESPONSE)

    def test_crawl_response_crawl_raised_exception(self):
        ex = Exception()
        cr = spider.CrawlResponseCrawlRaisedException(ex)
        self.assertCoreResponse(
            cr,
            spider.CrawlResponse.SC_CRAWL_RAISED_EXCEPTION)

    def test_crawl_response_ctr_raised_exception(self):
        ex = Exception()
        cr = spider.CrawlResponseCtrRaisedException(ex)
        self.assertCoreResponse(
            cr,
            spider.CrawlResponse.SC_CTR_RAISED_EXCEPTION)

    def test_crawl_response_spider_not_found(self):
        full_spider_class_name = uuid.uuid4().hex
        cr = spider.CrawlResponseSpiderNotFound(full_spider_class_name)
        self.assertCoreResponse(
            cr,
            spider.CrawlResponse.SC_SPIDER_NOT_FOUND)

    def test_status_code(self):
        cr = spider.CrawlResponseOk()
        self.assertEqual(cr.status_code, spider.CrawlResponse.SC_OK)
        del cr['_metadata']
        self.assertEqual(cr.status_code, spider.CrawlResponse.SC_UNKNOWN)


class TestSpider(unittest.TestCase):

    def test_crawl_with_no_crawl_method(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return {"url": "http://www.example.com"}
        my_spider = MySpider()
        with self.assertRaises(NotImplementedError):
            browser = None
            my_spider.crawl(browser)

    def test_spider_correctly_passes_crawl_args_and_returns(self):
        my_arg1 = str(uuid.uuid4())
        my_arg2 = str(uuid.uuid4())
        data = {
            'data1': str(uuid.uuid4()),
            'data2': str(uuid.uuid4()),
        }
        my_crawl_response = spider.CrawlResponseOk(data)

        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return {"url": "http://www.example.com"}

            def crawl(the_spider_self, browser, arg1, arg2):
                self.assertEqual(arg1, my_arg1)
                self.assertEqual(arg2, my_arg2)
                return my_crawl_response

        my_spider = MySpider()
        browser = None
        rv = my_spider.crawl(browser, my_arg1, my_arg2)
        self.assertTrue(rv is my_crawl_response)

    def test_spider_version(self):
        """Verify cloudfeaster.Spider.version()."""

        class MySpider(spider.Spider):
            pass

        module = sys.modules[self.__module__]
        source = inspect.getsource(module)
        source_hash = hashlib.sha256(source.encode('UTF-8'))
        expected_version = '%s:%s' % (source_hash.name, source_hash.hexdigest())
        self.assertEqual(expected_version, MySpider.version())


class HappyPathSpider(spider.Spider):

    @classmethod
    def get_metadata(cls):
        return {"url": "http://www.example.com"}

    def crawl(self, browser):
        return spider.CrawlResponseOk()


class CtrThrowsExceptionSpider(spider.Spider):

    @classmethod
    def get_metadata(cls):
        return {"url": "http://www.example.com"}

    def __init__(self):
        spider.Spider(self)
        raise Exception("oops!")

    def crawl(self, browser):
        return spider.CrawlResponseOk()


class CrawlThrowsExceptionSpider(spider.Spider):
    @classmethod
    def get_metadata(cls):
        return {"url": "http://www.example.com"}

    def crawl(self, browser):
        raise Exception()


class CrawlMethodThatReturnsUnexpectedTypeSpider(spider.Spider):
    @classmethod
    def get_metadata(cls):
        return {"url": "http://www.example.com"}

    def crawl(self, browser):
        return None


def get_browser_patch(url, *args, **kwargs):
    return mock.MagicMock()


class TestSpiderCrawler(unittest.TestCase):

    def test_ctr(self):
        full_spider_class_name = uuid.uuid4().hex
        spider_crawler = spider.SpiderCrawler(full_spider_class_name)
        self.assertEqual(spider_crawler.full_spider_class_name, full_spider_class_name)
        self.assertIsNone(spider_crawler.logging_file)
        self.assertIsNone(spider_crawler.chromedriver_log_file)
        self.assertIsNone(spider_crawler.screenshot_file)

    @mock.patch('cloudfeaster.spider.SpiderCrawler._get_browser', side_effect=get_browser_patch)
    def test_crawl_all_good_from_spider_name(self, mock_get_browser):
        full_spider_class_name = '%s.%s' % (__name__, HappyPathSpider.__name__)
        spider_crawler = spider.SpiderCrawler(full_spider_class_name)
        crawl_response = spider_crawler.crawl()
        self.assertEqual(
            crawl_response.status_code,
            spider.CrawlResponse.SC_OK)

    @mock.patch('cloudfeaster.spider.SpiderCrawler._get_browser', side_effect=get_browser_patch)
    def test_crawl_all_good_from_spider_class(self, mock_get_browser):
        spider_crawler = spider.SpiderCrawler(HappyPathSpider)
        crawl_response = spider_crawler.crawl()
        self.assertEqual(
            crawl_response.status_code,
            spider.CrawlResponse.SC_OK)

    @mock.patch('cloudfeaster.spider.SpiderCrawler._get_browser', side_effect=get_browser_patch)
    def test_spider_not_found_from_name(self, mock_get_browser):
        full_spider_class_name = '%s.%s' % (__name__, 'NoSuchSpiderKnownToMan')
        spider_crawler = spider.SpiderCrawler(full_spider_class_name)
        crawl_response = spider_crawler.crawl()
        self.assertTrue(isinstance(crawl_response, spider.CrawlResponse))
        self.assertEqual(
            crawl_response.status_code,
            spider.CrawlResponse.SC_SPIDER_NOT_FOUND)

    @mock.patch('cloudfeaster.spider.SpiderCrawler._get_browser', side_effect=get_browser_patch)
    def test_walk_with_spider_ctr_that_raises_exception(self, mock_get_browser):
        full_spider_class_name = '%s.%s' % (__name__, CtrThrowsExceptionSpider.__name__)
        spider_crawler = spider.SpiderCrawler(full_spider_class_name)
        crawl_response = spider_crawler.crawl()
        self.assertTrue(isinstance(crawl_response, spider.CrawlResponse))
        self.assertEqual(
            crawl_response.status_code,
            spider.CrawlResponse.SC_CTR_RAISED_EXCEPTION)

    @mock.patch('cloudfeaster.spider.SpiderCrawler._get_browser', side_effect=get_browser_patch)
    def test_walk_with_crawl_method_that_raises_exception(self, mock_get_browser):
        full_spider_class_name = '%s.%s' % (__name__, CrawlThrowsExceptionSpider.__name__)
        spider_crawler = spider.SpiderCrawler(full_spider_class_name)
        crawl_response = spider_crawler.crawl()
        self.assertTrue(isinstance(crawl_response, spider.CrawlResponse))
        self.assertEqual(
            crawl_response.status_code,
            spider.CrawlResponse.SC_CRAWL_RAISED_EXCEPTION)

    @mock.patch('cloudfeaster.spider.SpiderCrawler._get_browser', side_effect=get_browser_patch)
    def test_walk_with_crawl_method_with_invalid_return_type(self, mock_get_browser):
        full_spider_class_name = '%s.%s' % (__name__, CrawlMethodThatReturnsUnexpectedTypeSpider.__name__)
        spider_crawler = spider.SpiderCrawler(full_spider_class_name)
        crawl_response = spider_crawler.crawl()
        self.assertTrue(isinstance(crawl_response, spider.CrawlResponse))
        self.assertEqual(
            crawl_response.status_code,
            spider.CrawlResponse.SC_INVALID_CRAWL_RETURN_TYPE)

    @mock.patch('cloudfeaster.spider.SpiderCrawler._get_browser', side_effect=get_browser_patch)
    def test_crawl_metadata_spider(self, mock_get_browser):
        full_spider_class_name = '%s.%s' % (__name__, HappyPathSpider.__name__)
        spider_crawler = spider.SpiderCrawler(full_spider_class_name)
        crawl_response = spider_crawler.crawl()
        self.assertEqual(
            crawl_response.status_code,
            spider.CrawlResponse.SC_OK)
        self.assertIn('_metadata', crawl_response)
        self.assertIn('spider', crawl_response['_metadata'])
        self.assertIn('name', crawl_response['_metadata']['spider'])
        self.assertIn('version', crawl_response['_metadata']['spider'])

    @mock.patch('cloudfeaster.spider.SpiderCrawler._get_browser', side_effect=get_browser_patch)
    def test_crawl_metadata_crawl_time(self, mock_get_browser):
        full_spider_class_name = '%s.%s' % (__name__, HappyPathSpider.__name__)
        spider_crawler = spider.SpiderCrawler(full_spider_class_name)
        crawl_response = spider_crawler.crawl()
        self.assertEqual(
            crawl_response.status_code,
            spider.CrawlResponse.SC_OK)
        self.assertIn('_metadata', crawl_response)
        self.assertIn('crawlTime', crawl_response['_metadata'])
        self.assertIn('started', crawl_response['_metadata']['crawlTime'])
        self.assertIn('durationInMs', crawl_response['_metadata']['crawlTime'])


class TestSpiderMetadata(unittest.TestCase):

    def test_spider_not_implementing_get_metadata(self):
        class MySpider(spider.Spider):
            pass
        with self.assertRaises(NotImplementedError):
            MySpider.get_metadata()

    def test_get_validated_metadata_when_spider_not_implementing_get_metadata(self):
        class MySpider(spider.Spider):
            pass
        with self.assertRaises(NotImplementedError):
            MySpider.get_validated_metadata()

    def test_get_validated_metadata_when_spider_returns_invalid_get_metadata(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return "abc\ndef"

        with self.assertRaises(spider.SpiderMetadataError):
            MySpider.get_validated_metadata()

    def test_get_validated_metadata_when_spider_returns_none_for_get_metadata(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return None

        with self.assertRaises(spider.SpiderMetadataError):
            MySpider.get_validated_metadata()

    def test_get_validated_metadata_spider_with_no_crawl_method(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return {"url": "http://www.google.com"}

        reg_exp_pattern = (
            r"Spider class 'MySpider' has invalid metadata - "
            r"crawl\(\) method arg names not found"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_get_validated_metadata_spider_with_crawl_args_and_factor_names_mismatch(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "identifyingFactors": {
                        "memberId": {
                            "pattern": r"^[^\s]+$",
                        },
                    },
                    "authenticatingFactors": {
                        "password": {
                            "pattern": r"^[^\s]+$",
                        },
                    },
                }
                return rv

            def crawl(self, member_id):
                return None

        reg_exp_pattern = (
            r"Spider class 'MySpider' has invalid metadata - "
            r"crawl\(\) arg names and factor names don't match"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            try:
                MySpider.get_validated_metadata()
            except Exception as ex:
                raise ex

    def test_get_metadata_factors_and_factor_display_order_do_not_match(self):
        expected_metadata = {
            "url": "http://www.google.com",
            "identifyingFactors": {
                "memberId": {
                    "pattern": r"^[^\s]+$",
                },
            },
            "authenticatingFactors": {
                "password": {
                    "pattern": r"^[^\s]+$",
                },
            },
            "factorDisplayOrder": [
                "member_id_I_AM_THE_PROBLEM",
                "password",
            ]
        }

        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return expected_metadata

            def crawl(self, browser, member_id, password):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "factors and factor display order don't match"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_get_metadata_multiple_categories_specified_all_good(self):
        class MySpider(spider.Spider):
            metadata = {
                "categories": ["1", "2", "3"],
                "absoluteFilename": sys.modules[type(self).__module__].__file__,
                "url": "http://www.google.com",
                "ttl": "90s",
                "paranoiaLevel": "high",
                "maxConcurrentCrawls": 5,
                "maxCrawlTime": "45s",
                "identifyingFactors": {
                    "memberId": {
                        "pattern": r"^[^\s]+$",
                    },
                },
                "authenticatingFactors": {
                    "password": {
                        "pattern": r"^[^\s]+$",
                    },
                },
                "factorDisplayOrder": [
                    "memberId",
                    "password",
                ],
                "factorDisplayNames": {
                    "memberId": {
                        "": "memberId",
                    },
                    "password": {
                        "": "password",
                    },
                }
            }

            @classmethod
            def get_metadata(cls):
                cls.metadata["fullyQualifiedClassName"] = "{module}.{cls}".format(
                    module=cls.__module__,
                    cls=cls.__name__)
                return cls.metadata

            def crawl(self, browser, member_id, password):
                return None

        self.assertEqual(
            MySpider.metadata,
            MySpider.get_validated_metadata())

    def test_get_metadata_all_specified_all_good(self):
        class MySpider(spider.Spider):
            metadata = {
                "categories": ["cloudfeaster"],
                "absoluteFilename": sys.modules[type(self).__module__].__file__,
                "url": "http://www.google.com",
                "ttl": "90s",
                "paranoiaLevel": "high",
                "maxConcurrentCrawls": 5,
                "maxCrawlTime": "45s",
                "identifyingFactors": {
                    "memberId": {
                        "pattern": r"^[^\s]+$",
                    },
                },
                "authenticatingFactors": {
                    "password": {
                        "pattern": r"^[^\s]+$",
                    },
                },
                "factorDisplayOrder": [
                    "memberId",
                    "password",
                ],
                "factorDisplayNames": {
                    "memberId": {
                        "": "memberId",
                    },
                    "password": {
                        "": "password",
                    },
                }
            }

            @classmethod
            def get_metadata(cls):
                cls.metadata["fullyQualifiedClassName"] = "{module}.{cls}".format(
                    module=cls.__module__,
                    cls=cls.__name__)
                return cls.metadata

            def crawl(self, browser, member_id, password):
                return None

        self.assertEqual(
            MySpider.metadata,
            MySpider.get_validated_metadata())

    def test_get_metadata_no_display_names_specified(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return {
                    "url": "http://www.google.com",
                    "identifyingFactors": {
                        "memberId": {
                            "pattern": r"^[^\s]+$",
                        },
                    },
                    "authenticatingFactors": {
                        "password": {
                            "pattern": r"^[^\s]+$",
                        },
                    },
                    "factorDisplayOrder": [
                        "memberId",
                        "password",
                    ]
                }

            def crawl(self, browser, member_id, password):
                return None

        metadata = MySpider.get_validated_metadata()
        self.assertIsNotNone(metadata)

        factor_display_names = metadata['factorDisplayNames']

        factor_names = list(metadata['authenticatingFactors'].keys()) + list(metadata['identifyingFactors'].keys())
        expected_factor_display_names = {}
        for factor_name in factor_names:
            expected_factor_display_names[factor_name] = {'': factor_name}

        self.assertEqual(factor_display_names, expected_factor_display_names)

    def test_get_metadata_unknown_factor_in_factor_display_names(self):
        class MySpider(spider.Spider):
            metadata = {
                "url": "http://www.google.com",
                "identifyingFactors": {
                    "memberId": {
                        "pattern": r"^[^\s]+$",
                    },
                },
                "authenticatingFactors": {
                    "password": {
                        "pattern": r"^[^\s]+$",
                    },
                },
                "factorDisplayOrder": [
                    "memberId",
                    "password",
                ],
                "factorDisplayNames": {
                },
            }

            @classmethod
            def get_metadata(cls):
                return cls.metadata

            def crawl(self, browser, member_id, password):
                return None

        #
        # this should work just fine!
        #
        MySpider.get_validated_metadata()

        #
        # now create the error and verify get_validated_metadata()
        # catches the problem
        #
        MySpider.metadata["factorDisplayNames"]["bindle"] = {"": "berry"}
        reg_exp_pattern = (
            r"Spider class 'MySpider' has invalid metadata - "
            r"unknown factor\(s\) in factor display names"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_get_metadata_misspelled_factor_in_factor_display_names(self):
        class MySpider(spider.Spider):
            metadata = {
                "url": "http://www.google.com",
                "identifyingFactors": {
                    "memberId": {
                        "pattern": r"^[^\s]+$",
                    },
                },
                "authenticatingFactors": {
                    "password": {
                        "pattern": r"^[^\s]+$",
                    },
                },
                "factorDisplayOrder": [
                    "memberId",
                    "password",
                ],
                "factorDisplayNames": {
                    "memberId": {
                        "": "member ID",
                    },
                    "password": {
                        "": "password",
                    },
                },
            }

            @classmethod
            def get_metadata(cls):
                return cls.metadata

            def crawl(self, browser, member_id, password):
                return None

        #
        # this should work just fine!
        #
        MySpider.get_validated_metadata()

        #
        # now create the error and verify get_validated_metadata()
        # catches the problem
        #
        MySpider.metadata["factorDisplayNames"]["Password"] = MySpider.metadata["factorDisplayNames"]["password"]
        del MySpider.metadata["factorDisplayNames"]["password"]
        reg_exp_pattern = (
            r"Spider class 'MySpider' has invalid metadata - "
            r"unknown factor\(s\) in factor display names"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_url_for_spider_not_implementing_get_metadata(self):
        class MySpider(spider.Spider):
            pass
        with self.assertRaises(NotImplementedError):
            my_spider = MySpider()
            my_spider.url

    def test_url_all_good(self):
        expected_url = "http://www.google.com"

        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": expected_url,
                }
                return rv

            def crawl(self, browser):
                return None
        my_spider = MySpider()
        self.assertEqual(my_spider.url, expected_url)

    def test_ttl_invalid_type(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "ttl": 99,
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "99 is not of type 'string'"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_ttl_too_small(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "ttl": "0s",
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "'0s' does not match '.*'"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_ttl_all_good(self):
        class MySpider(spider.Spider):
            ttl = "3m"

            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "ttl": cls.ttl,
                }
                return rv

            def crawl(self, browser):
                return None

        metadata = MySpider.get_validated_metadata()
        self.assertTrue("ttl" in metadata)
        self.assertEqual(metadata["ttl"], MySpider.ttl)

    def test_ttl_default_value(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                }
                return rv

            def crawl(self, browser):
                return None

        metadata = MySpider.get_validated_metadata()
        self.assertTrue("ttl" in metadata)
        self.assertEqual(metadata["ttl"], "60s")

    def test_max_concurrent_crawls_invalid_type(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "maxConcurrentCrawls": "dave_was_here",
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "'dave_was_here' is not of type 'integer'"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_max_concurrent_crawls_value_too_low(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "maxConcurrentCrawls": 0,
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "0 is less than the minimum of 1"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_max_concurrent_crawls_value_too_high(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "maxConcurrentCrawls": 50,
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "50 is greater than the maximum of 25"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_max_concurrent_crawls_all_good(self):
        expected_max_concurrent_crawls = 1

        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "maxConcurrentCrawls": expected_max_concurrent_crawls,
                }
                return rv

            def crawl(self, browser):
                return None

        self.assertEqual(
            MySpider.get_validated_metadata()["maxConcurrentCrawls"],
            expected_max_concurrent_crawls)

    def test_max_concurrent_crawls_default_value(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                }
                return rv

            def crawl(self, browser):
                return None

        self.assertEqual(
            MySpider.get_validated_metadata()["maxConcurrentCrawls"],
            3)

    def test_max_crawl_time_invalid_type(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "maxCrawlTime": 60,
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "60 is not of type 'string'"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_max_crawl_too_small(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "maxCrawlTime": "0s",
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "'0s' does not match '.+'"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_max_crawl_time_happy_path(self):
        expected_value = "54s"

        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "maxCrawlTime": expected_value,
                }
                return rv

            def crawl(self, browser):
                return None

        self.assertEqual(
            MySpider.get_validated_metadata()["maxCrawlTime"],
            expected_value)

    def test_max_crawl_time_default_value(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                }
                return rv

            def crawl(self, browser):
                return None

        self.assertEqual(
            MySpider.get_validated_metadata()["maxCrawlTime"],
            "30s")

    def test_paranoia_invalid_type(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "paranoiaLevel": 1,
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            r"Spider class 'MySpider' has invalid metadata - "
            r"1 is not of type 'string'"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_paranoia_invalid_value(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "paranoiaLevel": "dave_was_here",
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            r"Spider class 'MySpider' has invalid metadata - "
            r"'dave_was_here' is not one of \['low', 'medium', 'high'\]"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_paranoia_invalid_all_good(self):
        expected_paranoia_level = "low"

        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "paranoiaLevel": expected_paranoia_level,
                }
                return rv

            def crawl(self, browser):
                return None

        self.assertEqual(
            MySpider.get_validated_metadata()["paranoiaLevel"],
            expected_paranoia_level)

    def test_abstract_base_class_with_crawl_method(self):
        class AbstractBaseClassWithCrawlMethodSpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return {
                    "identifyingFactors": {
                        "username": {
                            "pattern": r"^[^\s]+$",
                        }
                    },
                    "authenticatingFactors": {
                        "password": {
                            "pattern": r"^[^\s]+$",
                        }
                    },
                }

            def crawl(self, browser, username, password):
                return None

        class MySpider(AbstractBaseClassWithCrawlMethodSpider):
            @classmethod
            def get_metadata(cls):
                rv = AbstractBaseClassWithCrawlMethodSpider.get_metadata()
                rv["url"] = "http://www.google.com"
                return rv

        validated_metadata = MySpider.get_validated_metadata()
        self.assertIsNotNone(validated_metadata)
        self.assertEqual(
            validated_metadata['factorDisplayOrder'],
            ['username', 'password'])


class TestSpiderMetadataError(unittest.TestCase):

    def test_ctr_with_default_args(self):
        class MySpider(spider.Spider):
            pass
        ex = spider.SpiderMetadataError(MySpider)

        fmt = "Spider class '%s' has invalid metadata"
        self.assertEqual(
            str(ex),
            fmt % (MySpider.__name__))

    def test_ctr_with_message_detail(self):
        class MySpider(spider.Spider):
            pass

        message_detail = "dave was here"

        ex = spider.SpiderMetadataError(
            MySpider,
            message_detail=message_detail)

        fmt = "Spider class '%s' has invalid metadata - %s"
        self.assertEqual(
            str(ex),
            fmt % (MySpider.__name__, message_detail))

    def test_ctr_with_exception(self):
        class MySpider(spider.Spider):
            pass

        other_ex = Exception("dave was here")

        ex = spider.SpiderMetadataError(
            MySpider,
            ex=other_ex)

        fmt = "Spider class '%s' has invalid metadata - %s"
        self.assertEqual(
            str(ex),
            fmt % (MySpider.__name__, str(other_ex)))


class TestCLICrawlArgs(unittest.TestCase):

    def test_number_factors_matches_number_cl_args(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return {
                    "url": "http://www.google.com",
                    "identifyingFactors": {
                        "memberId": {
                            "pattern": r"^[^\s]+$",
                        },
                    },
                    "authenticatingFactors": {
                        "password": {
                            "pattern": r"^[^\s]+$",
                        },
                    },
                }

            def crawl(self, browser, member_id, password):
                return spider.CrawlResponseOk()

        validated_metadata = MySpider.get_validated_metadata()
        factors = validated_metadata["factorDisplayOrder"]

        patched_sys_dot_argv = ["my_spider.py", "12345", "secret"]
        self.assertEqual(
            len(factors),
            len(patched_sys_dot_argv) - 1)

        with mock.patch.object(sys, "argv", patched_sys_dot_argv):
            crawl_args = spider.CLICrawlArgs(MySpider)
            self.assertEqual(patched_sys_dot_argv[1:], crawl_args)

    def test_at_least_one_cl_arg_not_matching_number_factors(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return {
                    "url": "http://www.google.com",
                    "identifyingFactors": {
                        "memberId": {
                            "pattern": r"^[^\s]+$",
                        },
                    },
                    "authenticatingFactors": {
                        "password": {
                            "pattern": r"^[^\s]+$",
                        },
                    },
                }

            def crawl(self, browser, member_id, password):
                return spider.CrawlResponseOk()

        validated_metadata = MySpider.get_validated_metadata()
        factors = validated_metadata["factorDisplayOrder"]

        patched_sys_dot_argv = ["my_spider.py", "12345"]

        self.assertNotEqual(
            len(factors),
            len(patched_sys_dot_argv) - 1)

        with mock.patch.object(sys, "argv", patched_sys_dot_argv):
            mock_sys_dot_exit = mock.Mock()
            with mock.patch("sys.exit", mock_sys_dot_exit):
                spider.CLICrawlArgs(MySpider)
                mock_sys_dot_exit.assert_called_once_with(1)

    def test_prompt_for_all_crawl_args(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return {
                    "url": "http://www.google.com",
                    "identifyingFactors": {
                        "fruit": {
                            "enum": [
                                "apple",
                                "pear",
                                "pie",
                            ]
                        },
                        "memberId": {
                            "pattern": r"^[^\s]+$",
                        },
                    },
                    "authenticatingFactors": {
                        "password": {
                            "pattern": r"^[^\s]+$",
                        },
                    },
                }

            def crawl(self, browser, fruit, member_id, password):
                return spider.CrawlResponseOk()

        validated_metadata = MySpider.get_validated_metadata()
        factors = validated_metadata["factorDisplayOrder"]

        identifying_factors = validated_metadata["identifyingFactors"]
        authenticating_factors = validated_metadata["authenticatingFactors"]

        patched_sys_dot_argv = ["my_spider.py"]
        with mock.patch.object(sys, "argv", patched_sys_dot_argv):
            mock_sys_stdout_write = mock.Mock()
            with mock.patch("sys.stdout.write", mock_sys_stdout_write):
                mock_sys_stdin = mock.Mock()
                mock_sys_stdin.readline.return_value = "2"
                with mock.patch("sys.stdin", mock_sys_stdin):
                    mock_getpass_getpass = mock.Mock()
                    mock_getpass_getpass.return_value = "abc"
                    with mock.patch("getpass.getpass", mock_getpass_getpass):
                        crawl_args = spider.CLICrawlArgs(MySpider)

                        self.assertIsNotNone(crawl_args)

                        self.assertEqual(
                            len(factors),
                            len(crawl_args))

                        self.assertEqual(
                            mock_sys_stdin.readline.call_args_list,
                            len(identifying_factors) * [mock.call()])

                        self.assertEqual(
                            mock_getpass_getpass.call_args_list,
                            len(authenticating_factors) * [mock.call("")])

    def _assertMockNotCalled(self, mock):
        self.assertEqual(mock.call_args_list, [])

    def test_prompt_for_all_crawl_args_with_no_crawl_args_required(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                return {"url": "http://www.google.com"}

            def crawl(self, browser):
                return spider.CrawlResponseOk()

        validated_metadata = MySpider.get_validated_metadata()
        factors = validated_metadata["factorDisplayOrder"]
        self.assertEqual(0, len(factors))

        patched_sys_dot_argv = ["my_spider.py"]
        with mock.patch.object(sys, "argv", patched_sys_dot_argv):
            mock_sys_stdout_write = mock.Mock()
            with mock.patch("sys.stdout.write", mock_sys_stdout_write):
                mock_sys_stdin = mock.Mock()
                with mock.patch("sys.stdin", mock_sys_stdin):
                    mock_getpass_getpass = mock.Mock()
                    with mock.patch("getpass.getpass", mock_getpass_getpass):
                        crawl_args = spider.CLICrawlArgs(MySpider)
                        self.assertIsNotNone(crawl_args)
                        self.assertEqual(0, len(crawl_args))
                        self._assertMockNotCalled(mock_getpass_getpass)
                        self._assertMockNotCalled(mock_sys_stdin)
                        self._assertMockNotCalled(mock_sys_stdout_write)


@attr('integration')
class TestBrowser(unittest.TestCase):
    """A series of unit tests that validate ```spider.Browser```."""

    @classmethod
    def setUpClass(cls):
        cls._http_server = HTTPServer()
        cls._http_server.start()

    @classmethod
    def tearDownClass(cls):
        cls._http_server = None

    @attr('quick')
    def test_get_chrome_options_default(self):
        with mock.patch.dict('os.environ', {}, clear=True):
            paranoia_level = 'low'
            chrome_options = spider.Browser.get_chrome_options(paranoia_level)
            self.assertIsNotNone(chrome_options)
            self.assertEqual(
                chrome_options.binary_location,
                '')
            self.assertEqual(
                chrome_options.arguments,
                [
                    '--headless',
                    '--window-size=1280x1024',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--single-process',
                    '--disable-dev-shm-usage',
                    '--user-agent=%s' % cloudfeaster_extension.user_agent(),
                ])

    @attr('quick')
    def test_get_chrome_options_clf_chrome_env_var(self):
        binary_location = uuid.uuid4().hex
        with mock.patch.dict('os.environ', {'CLF_CHROME': binary_location}, clear=True):
            paranoia_level = 'low'
            chrome_options = spider.Browser.get_chrome_options(paranoia_level)
            self.assertIsNotNone(chrome_options)
            self.assertEqual(
                chrome_options.binary_location,
                binary_location)

    @attr('quick')
    def test_get_chrome_options_clf_chrome_options_env_var(self):
        arguments = [
            '--%s' % uuid.uuid4().hex,
            '--%s=%s' % (uuid.uuid4().hex, uuid.uuid4().hex),
            '--%s' % uuid.uuid4().hex,
        ]
        with mock.patch.dict('os.environ', {'CLF_CHROME_OPTIONS': '|'.join(arguments)}, clear=True):
            paranoia_level = 'low'
            chrome_options = spider.Browser.get_chrome_options(paranoia_level)
            self.assertIsNotNone(chrome_options)
            self.assertEqual(
                chrome_options.binary_location,
                '')
            self.assertEqual(
                chrome_options.arguments,
                arguments)

    @attr('quick')
    def test_get_chrome_options_proxy(self):
        paranoia_level = 'low'

        proxy_host = uuid.uuid4().hex
        proxy_port = 4242

        def my_proxy_patch(my_paranoia_level):
            self.assertEqual(paranoia_level, my_paranoia_level)
            return (proxy_host, proxy_port)

        with mock.patch.dict('os.environ', {}, clear=True):
            with mock.patch('cloudfeaster_extension.proxy', my_proxy_patch):
                chrome_options = spider.Browser.get_chrome_options(paranoia_level)
                self.assertIsNotNone(chrome_options)
                self.assertEqual(
                    chrome_options.binary_location,
                    '')
                self.assertEqual(
                    chrome_options.arguments,
                    [
                        '--headless',
                        '--window-size=1280x1024',
                        '--no-sandbox',
                        '--disable-gpu',
                        '--disable-software-rasterizer',
                        '--single-process',
                        '--disable-dev-shm-usage',
                        '--user-agent=%s' % cloudfeaster_extension.user_agent(),
                        '--proxy-server=%s:%d' % (proxy_host, proxy_port),
                    ])

    @attr('quick')
    def test_find_element_by_xpath_all_good(self):
        html = (
            '<html>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<h1 id=42>Dave Was Here!!!</h1>'
            '</body>'
            '</html>'
        )
        page = "testFindElementByXPathAllGood.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        paranoia_level = 'low'
        with spider.Browser(url, paranoia_level, None) as browser:
            xpath = "//h1[@id='42']"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)


@attr('integration')
class TestWebElement(unittest.TestCase):
    """A series of unit tests that validate ```spider.WebElement```."""

    @classmethod
    def setUpClass(cls):
        cls._http_server = HTTPServer()
        cls._http_server.start()

    @classmethod
    def tearDownClass(cls):
        cls._http_server = None

    def test_get_text_get_int_and_get_float(self):
        html = (
            '<html>\n'
            '<title>Dave Was Here!!!</title>\n'
            '<body>\n'
            '<h1>42</h1>\n'
            '<h1> 42.43 </h1>\n'
            '<h1> miles 1,342.43 ### </h1>\n'
            '<h1> this\n'
            'is\n'
            '666\n'
            'over many   lines\n'
            'and has 2\n'
            'numbers in one element\n'
            '</h1>\n'
            '</body>\n'
            '</html>'
        )
        page = "testGetTextGetIntAndGetFloat.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        paranoia_level = 'low'
        with spider.Browser(url, paranoia_level, None) as browser:
            xpath = "//h1[contains(text(),'42')]"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            number = element.get_int()
            self.assertIsNotNone(number)
            self.assertEqual(int, type(number))
            self.assertEqual(42, number)
            number = element.get_float()
            self.assertIsNotNone(number)
            self.assertEqual(float, type(number))
            self.assertEqual(42.0, number)

            xpath = "//h1[contains(text(),'42.43')]"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            number = element.get_float()
            self.assertIsNotNone(number)
            self.assertEqual(float, type(number))
            self.assertEqual(42.43, number)

            xpath = "//h1[contains(text(),'1,342.43')]"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            number = element.get_float()
            self.assertIsNotNone(number)
            self.assertEqual(float, type(number))
            self.assertEqual(1342.43, number)

            xpath = "//h1[contains(text(),'666')]"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            reg_ex = re.compile(
                r".*this\s+is\s+(?P<number>\d+)\s+over.*",
                re.IGNORECASE | re.DOTALL)
            number = element.get_int(reg_ex)
            self.assertIsNotNone(number)
            self.assertEqual(int, type(number))
            self.assertEqual(666, number)

            reg_ex = re.compile(
                r".*and\s+has\s+(?P<number>\d+)\s+numbers.*",
                re.IGNORECASE | re.DOTALL)
            number = element.get_int(reg_ex)
            self.assertIsNotNone(number)
            self.assertEqual(int, type(number))
            self.assertEqual(2, number)

            reg_ex = re.compile(
                r".*this\s+is\s+(?P<one>\d+)\s+over.*and\s+has\s+(?P<two>\d+)\s+numbers.*",
                re.IGNORECASE | re.DOTALL)
            number = element.get_int(reg_ex)
            self.assertIsNone(number)

            reg_ex = re.compile(
                r"NO MATCH HERE (?P<number>\d+)",
                re.IGNORECASE | re.DOTALL)
            number = element.get_int(reg_ex)
            self.assertIsNone(number)

    def test_get_selected_and_select_by_visible_text(self):
        html = (
            '<html>'
            '<head>'
            '<script type="text/javascript">'
            'function deselect_all_options()'
            '{'
            '   document.getElementById("select_element_id").selectedIndex=-1;'
            '}'
            '</script>'
            '</head>'
            '<title>Dave Was Here!!!</title>'
            '<body onload="deselect_all_options()">'
            '<select id="select_element_id">'
            '    <option value="AB" >Alberta</option>'
            '    <option value="BC" >British Columbia</option>'
            '    <option value="MB" >Manitoba</option>'
            '    <option value="NB" >New Brunswick</option>'
            '    <option value="NL" >Newfoundland and Labrador</option>'
            '    <option value="NS" >Nova Scotia</option>'
            '    <option value="ON" >Ontario</option>'
            '    <option value="PE" >Prince Edward Island</option>'
            '    <option value="QC" >Quebec</option>'
            '    <option value="SK" >Saskatchewan</option>'
            '</select>'
            '</body>'
            '</html>'
        )
        page = "testSelectByVisibleTextAndGetSelected.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        paranoia_level = 'low'
        with spider.Browser(url, paranoia_level, None) as browser:
            xpath = "//select[@id='select_element_id']"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)

            selected_option = element.get_selected()
            self.assertIsNone(selected_option)

            text_to_select = 'Ontario'
            element.select_by_visible_text(text_to_select)

            selected_option = element.get_selected()
            self.assertIsNotNone(selected_option)
            self.assertEqual(selected_option.get_text(), text_to_select)

            with self.assertRaises(selenium.common.exceptions.NoSuchElementException):
                element.select_by_visible_text("some option that won't be in the list")

    def test_get_selected_and_select_by_visible_text_on_non_select_element(self):
        html = (
            '<html>'
            '</head>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<h1 id=42>Dave Was Here!!!</h1>'
            '</body>'
            '</html>'
        )
        page = "testSelectByVisibleTextAndGetSelectedOnNonSelectElement.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        paranoia_level = 'low'
        with spider.Browser(url, paranoia_level, None) as browser:
            xpath = "//h1[@id='42']"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            with self.assertRaises(selenium.common.exceptions.UnexpectedTagNameException):
                element.get_selected()
            with self.assertRaises(selenium.common.exceptions.UnexpectedTagNameException):
                element.select_by_visible_text("something")


class TestSpiderDiscovery(unittest.TestCase):
    """A series of unit tests that validate ```spider.SpiderDiscovery```.

    :ADDRESS: not really super happy with this test. Feels like a lot of hard coding
    and assumptions. Maybe not but just feels like that.
    """

    def test_spiders_no_samples(self):
        importlib.import_module('cloudfeaster.samples')
        importlib.import_module('cloudfeaster.samples.pypi')
        importlib.import_module('cloudfeaster.samples.pythonwheels')
        importlib.import_module('cloudfeaster.samples.xe_exchange_rates')

        importlib.import_module('cloudfeaster.tests.some_test_spiders')
        importlib.import_module('cloudfeaster.tests.some_test_spiders.abstract')
        importlib.import_module('cloudfeaster.tests.some_test_spiders.supersimpleconcrete')

        sd = spider.SpiderDiscovery()
        spiders_by_category = sd.discover()

        #
        # only expecting a certain set of categories
        #
        categories = list(spiders_by_category.keys())
        categories.sort()
        expected_categories = [
            'cloudfeaster',
            'fx_rates',
        ]
        expected_categories.sort()
        self.assertEqual(categories, expected_categories)

        spiders_by_spider_name = spiders_by_category['cloudfeaster']

        #
        # only expecting a certain set of spiders
        #
        fqcn_key = 'fullyQualifiedClassName'

        def is_sample(metadata):
            return metadata[fqcn_key].startswith('cloudfeaster.samples')

        spider_names = [metadata[fqcn_key] for metadata in spiders_by_spider_name.values() if is_sample(metadata)]
        spider_names.sort()

        expected_spider_names = [
            'cloudfeaster.samples.pypi.PyPISpider',
            'cloudfeaster.samples.pythonwheels.PythonWheelsSpider',
            'cloudfeaster.samples.xe_exchange_rates.XEExchangeRatesSpider',
        ]
        expected_spider_names.sort()

        self.assertEqual(spider_names, expected_spider_names)

        #
        # confirm available test spiders which explore concrete and abstract spider classes
        #
        fqcn_key = 'fullyQualifiedClassName'

        def is_test(metadata):
            return metadata[fqcn_key].startswith('cloudfeaster.tests.some_test_spiders')

        spider_names = [metadata[fqcn_key] for metadata in spiders_by_spider_name.values() if is_test(metadata)]
        spider_names.sort()

        expected_spider_names = [
            'cloudfeaster.tests.some_test_spiders.abstract.Spider',
            'cloudfeaster.tests.some_test_spiders.supersimpleconcrete.Spider',
        ]
        expected_spider_names.sort()

        self.assertEqual(spider_names, expected_spider_names)
