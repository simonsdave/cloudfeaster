#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys

from cloudfeaster import spider
from cloudfeaster import webdriver_spider


class PythonWheelsSpider(spider.Spider):

    @classmethod
    def get_metadata(cls):
        return {
            'url': 'https://pythonwheels.com/',
        }

    def crawl(self):
        with webdriver_spider.Browser(self.url) as browser:
            return self._crawl(browser)

    def _crawl(self, browser):
        data = {}

        rank = 1

        xpath = "//span[@ng-bind='package.name']"
        for package_name_element in browser.find_elements_by_xpath(xpath):
            package_name = package_name_element.get_text()

            link_element = package_name_element.find_element_by_xpath('..')
            link = link_element.get_attribute('href')

            data[package_name] = {
                'rank': rank,
                'link': link,
            }

            rank += 1
            if 10 < rank:
                break

        return spider.CrawlResponseOk(data)


if __name__ == '__main__':
    crawl_args = spider.CLICrawlArgs(PythonWheelsSpider)
    crawler = spider.SpiderCrawler(PythonWheelsSpider)
    crawl_result = crawler.crawl(*crawl_args)
    print json.dumps(crawl_result)
    sys.exit(1 if crawl_result._status_code else 0)
