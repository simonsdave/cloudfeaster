#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import json
import sys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from cloudfeaster import spider


class PythonWheelsSpider(spider.Spider):

    @classmethod
    def get_metadata(cls):
        return {
            'url': 'https://pythonwheels.com/',
        }

    def crawl(self, browser):
        ten_seconds = 10
        web_driver_wait = WebDriverWait(browser, ten_seconds)

        data = {}

        rank = 1

        xpath = "//span[@ng-bind='package.name']"
        package_name_elements = web_driver_wait.until(lambda browser: browser.find_elements(By.XPATH, xpath))
        for package_name_element in package_name_elements:
            package_name = package_name_element.get_text()

            link_element = package_name_element.find_element(By.XPATH, '..')
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
    print(json.dumps(crawl_result))
    sys.exit(1 if crawl_result.status_code else 0)
