#!/usr/bin/env python

import json

from cloudfeaster import spider
from cloudfeaster import webdriver_spider


class PyPISpider(spider.Spider):

    @classmethod
    def get_metadata_definition(cls):
        rv = {
            "url": "http://pypi-ranking.info/alltime",
        }
        return rv

    def crawl(self):
        with webdriver_spider.Browser(self.url) as browser:
            return self._crawl(browser)

    def _crawl(self, browser):

        data = {}
        rank = 1

        locator = "//span[@class='list_title']"
        title_elements = browser.find_elements_by_xpath(locator)
        for title_element in title_elements:
            module = title_element.get_text()
            locator = ".."
            link_element = title_element.find_element_by_xpath(locator)
            link = link_element.get_attribute("href")
            locator = "../../td[@class='count']/span"
            count_element = link_element.find_element_by_xpath(locator)
            count = count_element.get_int()

            data[module] = {
                "rank": rank,
                "link": link,
                "count": count,
            }

            rank += 1

        return spider.CrawlResponseOk(data)

if __name__ == "__main__":
    crawl_args = spider.CLICrawlArgs(PyPISpider)
    crawl_result = PyPISpider.walk(*crawl_args)
    print json.dumps(crawl_result, indent=4)
