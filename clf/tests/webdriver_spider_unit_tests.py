"""This module contains unit tests for the ```webdriver_spider``` module."""

import os
import sys
import unittest
import uuid

import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import spider
import webdriver_spider

class TestSpider(unittest.TestCase):

    def test_crawl_args_and_return_value_passed_correctly(self):

        self.my_url = "http://www.example.com"
        self.my_arg1 = str(uuid.uuid4())
        self.my_arg2 = str(uuid.uuid4())
        self.mock_browser = None

        def browser_class_patch():
            self.assertIsNone(self.mock_browser)
            self.mock_browser = mock.Mock()
            return self.mock_browser

        with mock.patch("webdriver_spider.Browser", browser_class_patch):

            self.crawl_rv = spider.CrawlResponse(spider.SC_OK)

            class MySpider(webdriver_spider.Spider):
                def crawl(my_spider_self, browser, arg1, arg2):
                    return self.crawl_rv

            my_spider = MySpider(self.my_url)
            walk_rv = my_spider.walk(self.my_arg1, self.my_arg2)
            self.assertIsNotNone(walk_rv)
            self.assertEqual(walk_rv, self.crawl_rv)

            self.assertIsNotNone(self.mock_browser)
            self.assertEqual(self.mock_browser.quit.call_count, 1)
