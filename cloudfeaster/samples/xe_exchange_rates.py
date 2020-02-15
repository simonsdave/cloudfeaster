#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

import json
import sys

import dateutil.parser
from selenium.webdriver.support.ui import WebDriverWait

from cloudfeaster import spider


class XEExchangeRatesSpider(spider.Spider):

    @classmethod
    def get_metadata(cls):
        return {
            'url': 'https://www.xe.com/?cn=cad',
        }

    def crawl(self, browser):
        ten_seconds = 10
        web_driver_wait = WebDriverWait(browser, ten_seconds)

        xpath = '//time'
        rates_on_element = web_driver_wait.until(lambda browser: browser.find_element_by_xpath(xpath))
        rates_on = dateutil.parser.parse(rates_on_element.get_text())
        data = {
            'ratesOn': rates_on.isoformat(),
            'rates': [
            ]
        }

        xpath = '//a[contains(@class, "rateChartLink")]'
        rate_elements = web_driver_wait.until(lambda browser: browser.find_elements_by_xpath(xpath))
        for rate_element in rate_elements:
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
    print(json.dumps(crawl_result))
    sys.exit(1 if crawl_result.status_code else 0)
