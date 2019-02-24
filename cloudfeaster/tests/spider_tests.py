"""This module contains unit tests for the ```spider``` module."""

import hashlib
import inspect
import mock
import sys
import unittest
import uuid

from .. import spider


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
        hash = hashlib.sha1(source)
        expected_version = '%s:%s' % (hash.name, hash.hexdigest())
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


def get_browser_patch(url):
    return mock.MagicMock()


class TestSpiderCrawler(unittest.TestCase):

    @mock.patch('cloudfeaster.spider.SpiderCrawler._get_browser', side_effect=get_browser_patch)
    def test_crawl_all_good_from_spider_name(self, mock_get_browser):
        full_spider_class_name = '%s.%s' % (__name__, HappyPathSpider.__name__)
        spider_crawler = spider.SpiderCrawler(full_spider_class_name)
        crawl_response = spider_crawler.crawl()
        print crawl_response
        self.assertEqual(
            crawl_response.status_code,
            spider.CrawlResponse.SC_OK)

    @mock.patch('cloudfeaster.spider.SpiderCrawler._get_browser', side_effect=get_browser_patch)
    def test_crawl_all_good_from_spider_class(self, mock_get_browser):
        spider_crawler = spider.SpiderCrawler(HappyPathSpider)
        crawl_response = spider_crawler.crawl()
        print crawl_response
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
            MySpider.get_validated_metadata()

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

    def test_get_metadata_all_specified_all_good(self):
        class MySpider(spider.Spider):
            metadata = {
                "url": "http://www.google.com",
                "ttlInSeconds": 90,
                "paranoiaLevel": "high",
                "maxConcurrentCrawls": 5,
                "maxCrawlTimeInSeconds": 10,
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

        factor_display_names = metadata["factorDisplayNames"]

        factor_names = metadata["authenticatingFactors"].keys() + \
            metadata["identifyingFactors"].keys()
        expected_factor_display_names = {}
        for factor_name in factor_names:
            expected_factor_display_names[factor_name] = {"": factor_name}

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

    def test_ttl_in_seconds_invalid_type(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "ttlInSeconds": 99.9,
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "99.9 is not of type u'integer'"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_ttl_in_seconds_value_too_small(self):
        class MySpider(spider.Spider):
            ttl_in_seconds = 60

            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "ttlInSeconds": cls.ttl_in_seconds,
                }
                return rv

            def crawl(self, browser):
                return None

        #
        # the all good scenario
        #
        MySpider.get_validated_metadata()

        #
        # change the ttl_in_seconds so it's smaller than it should be and
        # watch the errors fly
        #
        MySpider.ttl_in_seconds = 59

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "59 is less than the minimum of 60"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_ttl_in_seconds_value_too_big(self):
        class MySpider(spider.Spider):
            ttl_in_seconds = 60

            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "ttlInSeconds": cls.ttl_in_seconds,
                }
                return rv

            def crawl(self, browser):
                return None

        #
        # the all good scenario
        #
        MySpider.get_validated_metadata()

        #
        # change the ttl_in_seconds so it's smaller than it should be and
        # watch the errors fly
        #
        MySpider.ttl_in_seconds = 5 * 24 * 60 * 60  # = 5 days in seconds

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "432000 is greater than the maximum of 86400"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_ttl_all_good(self):
        class MySpider(spider.Spider):
            ttl_in_seconds = 87

            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "ttlInSeconds": cls.ttl_in_seconds,
                }
                return rv

            def crawl(self, browser):
                return None

        metadata = MySpider.get_validated_metadata()
        self.assertTrue("ttlInSeconds" in metadata)
        self.assertEqual(metadata["ttlInSeconds"], MySpider.ttl_in_seconds)

    def test_ttl_in_seconds_default_value(self):
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
        self.assertTrue("ttlInSeconds" in metadata)
        self.assertEqual(metadata["ttlInSeconds"], 60)

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
            "'dave_was_here' is not of type u'integer'"
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

    def test_max_crawl_time_in_seconds_invalid_type(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "maxCrawlTimeInSeconds": "dave_was_here",
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "'dave_was_here' is not of type u'integer'"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_max_crawl_time_in_seconds_too_low(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "maxCrawlTimeInSeconds": 0,
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "0 is less than the minimum of 5"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_max_crawl_time_in_seconds_too_high(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "maxCrawlTimeInSeconds": 100 * 60,
                }
                return rv

            def crawl(self, browser):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "6000 is greater than the maximum of 300"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            MySpider.get_validated_metadata()

    def test_max_crawl_time_in_seconds_happy_path(self):
        expected_value = 54

        class MySpider(spider.Spider):
            @classmethod
            def get_metadata(cls):
                rv = {
                    "url": "http://www.google.com",
                    "maxCrawlTimeInSeconds": expected_value,
                }
                return rv

            def crawl(self, browser):
                return None

        self.assertEqual(
            MySpider.get_validated_metadata()["maxCrawlTimeInSeconds"],
            expected_value)

    def test_max_crawl_time_in_seconds_default_value(self):
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
            MySpider.get_validated_metadata()["maxCrawlTimeInSeconds"],
            30)

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
            r"1 is not one of \[u'low', u'medium', u'high'\]"
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
            r"'dave_was_here' is not one of \[u'low', u'medium', u'high'\]"
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
            ex.message,
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
            ex.message,
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
            ex.message,
            fmt % (MySpider.__name__, other_ex.message))


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
        print factors

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
