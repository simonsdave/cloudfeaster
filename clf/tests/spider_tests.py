"""This module contains unit tests for the ```spider``` module."""

import hashlib
import inspect
import mock
import sys
import unittest
import uuid

from clf import spider


class TestCrawlResponse(unittest.TestCase):

    def test_ctr_with_just_status_code_ok(self):
        status_code = 42
        cr = spider.CrawlResponse(status_code)
        self.assertEqual(cr.status_code, status_code)
        self.assertIsNone(cr.data)
        self.assertIsNone(cr.status)

    def test_ctr_with_status_code_and_status_ok(self):
        status_code = 42
        status = str(uuid.uuid4())
        cr = spider.CrawlResponse(status_code, status=status)
        self.assertEqual(cr.status_code, status_code)
        self.assertIsNone(cr.data)
        self.assertEqual(cr.status, status)

    def test_ctr_with_status_code_status_and_data_ok(self):
        status_code = 42
        status = str(uuid.uuid4())
        data = {
            'data1': str(uuid.uuid4()),
            'data2': str(uuid.uuid4()),
        }
        cr = spider.CrawlResponse(status_code, data, status)
        self.assertEqual(cr.status_code, status_code)
        self.assertEqual(cr.data, data)
        self.assertEqual(cr.status, status)


class TestSpider(unittest.TestCase):

    def test_crawl_with_no_crawl_method(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                return {"url": "http://www.example.com"}
        my_spider = MySpider()
        with self.assertRaises(NotImplementedError):
            my_spider.crawl()

    def test_spider_correctly_passes_crawl_args_and_returns(self):
        my_arg1 = str(uuid.uuid4())
        my_arg2 = str(uuid.uuid4())
        my_crawl_response = spider.CrawlResponse(
            spider.CrawlResponse.SC_OK,
            {
                'data1': str(uuid.uuid4()),
                'data2': str(uuid.uuid4()),
            },
            "all ok!!!"
        )

        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                return {"url": "http://www.example.com"}
            def crawl(the_spider_self, arg1, arg2):
                self.assertEqual(arg1, my_arg1)
                self.assertEqual(arg2, my_arg2)
                return my_crawl_response

        my_spider = MySpider()
        rv = my_spider.crawl(my_arg1, my_arg2)
        self.assertIsNotNone(rv)
        self.assertEqual(type(rv), spider.CrawlResponse)
        self.assertEqual(rv, my_crawl_response)

    def test_spider_version(self):
        """Verify clf.Spider.version()."""

        class MySpider(spider.Spider):
            pass

        module = sys.modules[self.__module__]
        source = inspect.getsource(module)
        expected_version = hashlib.sha1(source)
        expected_version = expected_version.hexdigest()
        self.assertEqual(expected_version, MySpider.version())

    def test_walk_all_good(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                return {"url": "http://www.example.com"}
            def crawl(self):
                return spider.CrawlResponse(spider.CrawlResponse.SC_OK)
        rv = MySpider.walk()
        self.assertIsNotNone(rv)
        self.assertEqual(type(rv), spider.CrawlResponse)
        self.assertEqual(rv.status_code, spider.CrawlResponse.SC_OK)

    def test_walk_with_spider_ctr_that_raises_exception(self):
        class MySpider(spider.Spider):
            def __init__(self):
                spider.Spider(self)
                raise Exception("oops!")
            @classmethod
            def get_metadata_definition(cls):
                return {"url": "http://www.example.com"}
            def crawl(self):
                return spider.CrawlResponse(spider.CrawlResponse.SC_OK)
        rv = MySpider.walk()
        self.assertIsNotNone(rv)
        self.assertEqual(type(rv), spider.CrawlResponse)
        self.assertEqual(
            rv.status_code,
            spider.CrawlResponse.SC_SPIDER_CTR_THREW_EXCEPTION)

    def test_walk_with_crawl_method_that_raises_exception(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                return {"url": "http://www.example.com"}
            def crawl(self):
                raise Exception()
        rv = MySpider.walk()
        self.assertIsNotNone(rv)
        self.assertEqual(type(rv), spider.CrawlResponse)
        self.assertEqual(rv.status_code, spider.CrawlResponse.SC_CRAWL_THREW_EXCEPTION)

    def test_walk_with_crawl_method_with_invalid_return_type(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                return {"url": "http://www.example.com"}
            def crawl(self):
                return None
        rv = MySpider.walk()
        self.assertIsNotNone(rv)
        self.assertEqual(type(rv), spider.CrawlResponse)
        self.assertEqual(rv.status_code, spider.CrawlResponse.SC_INVALID_CRAWL_RETURN_TYPE)


class TestSpiderMetadata(unittest.TestCase):

    def test_spider_not_implementing_get_metadata_definition(self):
        class MySpider(spider.Spider):
            pass
        with self.assertRaises(NotImplementedError):
            MySpider.get_metadata_definition()

    def test_get_metadata_when_spider_not_implementing_get_metadata_definition(self):
        class MySpider(spider.Spider):
            pass
        with self.assertRaises(NotImplementedError):
            MySpider.get_metadata()

    def test_get_metadata_when_spider_returns_invalid_get_metadata_definition(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                return "abc\ndef"

        with self.assertRaises(spider.SpiderMetadataError):
            MySpider.get_metadata()

    def test_get_metadata_when_spider_returns_none_for_get_metadata_definition(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                return None

        with self.assertRaises(spider.SpiderMetadataError):
            MySpider.get_metadata()

    def test_get_metadata_spider_with_no_crawl_method(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                return {"url": "http://www.google.com"}

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "crawl\(\) not found"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            metadata = MySpider.get_metadata()

    def test_get_metadata_spider_with_crawl_args_and_factor_names_mismatch(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                rv = {
                    "url": "http://www.google.com",
                    "identifying_factors": {
                        "member_id": {
                            "pattern": "^[^\s]+$",
                        },
                    },
                    "authenticating_factors": {
                        "password": {
                            "pattern": "^[^\s]+$",
                        },
                    },
                }
                return rv

            def crawl(self, member_id):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "crawl\(\) arg names and factor names don't match"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            metadata = MySpider.get_metadata()

    def test_get_metadata_spider_with_crawl_args_and_explicit_factor_names_mismatch(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                rv = {
                    "url": "http://www.google.com",
                    "identifying_factors": {
                        "member_id": {
                            "pattern": "^[^\s]+$",
                        },
                    },
                    "authenticating_factors": {
                        "password": {
                            "pattern": "^[^\s]+$",
                        },
                    },
                    "factors": [
                        "member_id",
                    ],
                }
                return rv

            def crawl(self, member_id, password):
                return None

        reg_exp_pattern = (
            "Spider class 'MySpider' has invalid metadata - "
            "crawl\(\) arg names and explicit factor names don't match"
        )
        with self.assertRaisesRegexp(spider.SpiderMetadataError, reg_exp_pattern):
            metadata = MySpider.get_metadata()

    def test_get_metadata_all_specified_all_good(self):
        expected_metadata = {
            "url": "http://www.google.com",
            "identifying_factors": {
                "member_id": {
                    "pattern": "^[^\s]+$",
                },
            },
            "authenticating_factors": {
                "password": {
                    "pattern": "^[^\s]+$",
                },
            },
            "factors": [
                "member_id",
                "password",
            ],
        }

        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                return expected_metadata
            def crawl(self, member_id, password):
                return None

        metadata = MySpider.get_metadata()
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata, expected_metadata)

    def test_url_for_spider_not_implementing_get_metadata_definition(self):
        class MySpider(spider.Spider):
            pass
        with self.assertRaises(NotImplementedError):
            my_spider = MySpider()
            my_spider.url

    def test_url_all_good(self):
        expected_url = "http://www.google.com"
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                rv = {
                    "url": expected_url,
                }
                return rv
            def crawl(self):
                return None
        my_spider = MySpider()
        self.assertEqual(my_spider.url, expected_url)


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
            def get_metadata_definition(cls):
                rv = {
                    "url": "http://www.google.com",
                    "identifying_factors": {
                        "member_id": {
                            "pattern": "^[^\s]+$",
                        },
                    },
                    "authenticating_factors": {
                        "password": {
                            "pattern": "^[^\s]+$",
                        },
                    },
                }
                return rv
            def crawl(self, member_id, password):
                return spider.CrawlResponse(spider.CrawlResponse.SC_OK)

        factor_names = MySpider.get_metadata()["factors"]
        patched_sys_dot_argv = ["my_spider.py", "12345", "secret"]
        self.assertEqual(len(factor_names), len(patched_sys_dot_argv) - 1)
        with mock.patch.object(sys, "argv", patched_sys_dot_argv):
            crawl_args = spider.CLICrawlArgs(MySpider)
            self.assertEqual(patched_sys_dot_argv[1:], crawl_args)

    def test_at_least_one_cl_arg_not_matching_number_factors(self):
        class MySpider(spider.Spider):
            @classmethod
            def get_metadata_definition(cls):
                rv = {
                    "url": "http://www.google.com",
                    "identifying_factors": {
                        "member_id": {
                            "pattern": "^[^\s]+$",
                        },
                    },
                    "authenticating_factors": {
                        "password": {
                            "pattern": "^[^\s]+$",
                        },
                    },
                }
                return rv
            def crawl(self, member_id, password):
                return spider.CrawlResponse(spider.CrawlResponse.SC_OK)

        factor_names = MySpider.get_metadata()["factors"]
        patched_sys_dot_argv = ["my_spider.py", "12345"]
        self.assertNotEqual(len(factor_names), len(patched_sys_dot_argv) - 1)
        self.assertTrue(1 < len(patched_sys_dot_argv))
        with mock.patch.object(sys, "argv", patched_sys_dot_argv):
            mock_sys_dot_exit = mock.Mock()
            with mock.patch("sys.exit", mock_sys_dot_exit):
                spider.CLICrawlArgs(MySpider)
                mock_sys_dot_exit.assert_called_once_with(1)
