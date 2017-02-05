#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys

from cloudfeaster import spider
from cloudfeaster import webdriver_spider


class PyPISpider(spider.Spider):

    @classmethod
    def get_metadata(cls):
        return {
            'url': 'http://pypi-ranking.info/alltime',
        }

    def crawl(self):
        with webdriver_spider.Browser(self.url) as browser:
            return self._crawl(browser)

    def _crawl(self, browser):
        data = {}
        rank = 1
        xpath = "//span[@class='list_title']"
        title_elements = browser.find_elements_by_xpath(xpath)
        for title_element in title_elements:
            module = title_element.get_text()

            link_element = title_element.find_element_by_xpath('..')
            link = link_element.get_attribute('href')

            xpath = "../../td[@class='count']/span"
            count_element = link_element.find_element_by_xpath(xpath)
            count = count_element.get_int()

            data[module] = {
                'rank': rank,
                'link': link,
                'count': count,
            }

            rank += 1
            if 5 < rank:
                break

        return spider.CrawlResponseOk(data)


if __name__ == '__main__':
    crawl_args = spider.CLICrawlArgs(PyPISpider)
    crawler = spider.SpiderCrawler(PyPISpider)
    crawl_result = crawler.crawl(*crawl_args)
    print json.dumps(crawl_result)
    sys.exit(1 if crawl_result._status_code else 0)
