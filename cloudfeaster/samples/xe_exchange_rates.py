#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys

import dateutil.parser

from cloudfeaster import spider
from cloudfeaster import webdriver_spider


class XEExchangeRatesSpider(webdriver_spider.Spider):

    @classmethod
    def get_metadata(cls):
        return {
            'url': 'https://www.xe.com/?cn=cad',
        }

    def crawl(self):
        with self.get_browser(self.url) as browser:
            return self._crawl(browser)

    def _crawl(self, browser):
        rates_on_element = browser.find_element_by_xpath('//time')
        rates_on = dateutil.parser.parse(rates_on_element.get_text())
        data = {
            'ratesOn': rates_on.isoformat(),
            'rates': [
            ]
        }

        for rate_element in browser.find_elements_by_xpath('//a[contains(@class, "rateChartLink")]'):
            data['rates'].append({
                'rate': rate_element.get_float(),
                'from': rate_element.get_attribute('from'),
                'to': rate_element.get_attribute('to'),
            })

        return spider.CrawlResponseOk(data)


if __name__ == '__main__':
    crawl_args = spider.CLICrawlArgs(XEExchangeRatesSpider)
    crawler = spider.SpiderCrawler(XEExchangeRatesSpider)
    crawl_result = crawler.crawl(*crawl_args)
    print json.dumps(crawl_result)
    sys.exit(1 if crawl_result.status_code else 0)
