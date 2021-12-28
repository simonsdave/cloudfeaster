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
            'url': 'https://alpinelinux.org/releases/',
        }

    def crawl(self, browser):
        ten_seconds = 10
        web_driver_wait = WebDriverWait(browser, ten_seconds)

        data = {}

        xpath = "//div[@class='releases']/table/thead/tr/th"
        table_header_elements = web_driver_wait.until(lambda browser: browser.find_elements(By.XPATH, xpath))
        table_headers = [table_header_element.get_text() for table_header_element in table_header_elements]

        branch_index = table_headers.index('Branch')
        branch_date_index = table_headers.index('Branch date')
        end_of_support_index = table_headers.index('End of support')
        minor_releases_index = table_headers.index('Minor releases')

        xpath = "//div[@class='releases']/table/tbody/tr"
        release_elements = web_driver_wait.until(lambda browser: browser.find_elements(By.XPATH, xpath))
        for release_element in release_elements:
            release_child_elements = release_element.find_elements(By.XPATH, 'td')

            branch_element = release_child_elements[branch_index]
            branch = branch_element.get_text()
            if 'edge' == branch:
                continue

            url_elements = branch_element.find_elements(By.XPATH, 'a')
            url_element = url_elements[0]
            url = url_element.get_attribute('href')

            branch_date_element = release_child_elements[branch_date_index]
            branch_date = branch_date_element.get_text()

            end_of_support_element = release_child_elements[end_of_support_index]
            end_of_support = end_of_support_element.get_text()

            minor_releases_elements = release_child_elements[minor_releases_index].find_elements(By.XPATH, 'a')
            minor_releases = [minor_releases_element.get_text() for minor_releases_element in minor_releases_elements]

            data[branch] = {
                'date': branch_date,
                'eol': end_of_support,
                'url': url,
                'minorReleases': minor_releases,
            }

        return spider.CrawlResponseOk(data)


if __name__ == '__main__':
    crawl_args = spider.CLICrawlArgs(PythonWheelsSpider)
    crawler = spider.SpiderCrawler(PythonWheelsSpider)
    crawl_result = crawler.crawl(*crawl_args)
    print(json.dumps(crawl_result))
    sys.exit(1 if crawl_result.status_code else 0)
