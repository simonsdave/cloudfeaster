"""This module contains unit tests for the ```spider``` module."""

import os
import sys
import unittest
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import spider

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


class SpiderWithNoCrawlMethod(spider.Spider):
    pass


class SpiderWithCrawlMethodThatThrowsException(spider.Spider):

    def crawl(self):
        raise Exception()


class SpiderWithCrawlMethodThatReturnsNone(spider.Spider):

    def crawl(self):
        return None


class TestSpider(unittest.TestCase):

    def test_spider_ctr_sets_url_property(self):
        url = "http://www.example.com"
        my_spider = SpiderWithNoCrawlMethod("http://www.example.com")
        self.assertIsNotNone(my_spider.url)
        self.assertEqual(my_spider.url, url)

    def test_spider_with_no_crawl_method(self):
        url = "http://www.example.com"
        my_spider = SpiderWithNoCrawlMethod(url)
        rv = my_spider.walk()
        self.assertIsNotNone(rv)
        self.assertEqual(type(rv), spider.CrawlResponse)
        self.assertEqual(rv.status_code, spider.SC_CRAWL_NOT_IMPLEMENTED)

    def test_spider_with_crawl_method_that_raises_exception(self):
        url = "http://www.example.com"
        my_spider = SpiderWithCrawlMethodThatThrowsException(url)
        rv = my_spider.walk()
        self.assertIsNotNone(rv)
        self.assertEqual(type(rv), spider.CrawlResponse)
        self.assertEqual(rv.status_code, spider.SC_CRAWL_THREW_EXCEPTION)

    def test_spider_with_crawl_method_with_invalid_return_type(self):
        url = "http://www.example.com"
        my_spider = SpiderWithCrawlMethodThatReturnsNone(url)
        rv = my_spider.walk()
        self.assertIsNotNone(rv)
        self.assertEqual(type(rv), spider.CrawlResponse)
        self.assertEqual(rv.status_code, spider.SC_INVALID_CRAWL_RETURN_TYPE)
