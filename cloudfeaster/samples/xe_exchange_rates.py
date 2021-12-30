#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import json
import re
import sys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from cloudfeaster import spider

# parse patterns like "USD / CAD"
_currency_reg_ex = re.compile(
    r'^\s*(?P<from>[^\s]+)\s*/\s*(?P<to>[^\s]+)\s*$',
    flags=re.IGNORECASE)


class XEExchangeRatesSpider(spider.Spider):

    @classmethod
    def get_metadata(cls):
        return {
            'url': 'https://www.xe.com/currencycharts/',
            'categories': [
                cls.get_default_category(),
                'fx_rates',
            ],
        }

    def crawl(self, browser):
        data = {
            'rates': [
            ]
        }

        ten_seconds = 10
        web_driver_wait = WebDriverWait(browser, ten_seconds)

        xpath = '//h2[text()="Live Currency Rates"]/../table/tbody/tr'
        table_row_elements = web_driver_wait.until(lambda browser: browser.find_elements(By.XPATH, xpath))
        for table_row_element in table_row_elements:
            from_to_element = table_row_element.find_elements(By.XPATH, 'td[1]/a')[0]
            rate_element = table_row_element.find_elements(By.XPATH, 'td[2]')[0]
            from_to = from_to_element.get_text()
            match = _currency_reg_ex.match(from_to)
            data['rates'].append({
                'from': match.group('from'),
                'to': match.group('to'),
                'rate': rate_element.get_float(),
            })

        return spider.CrawlResponseOk(data)


if __name__ == '__main__':
    crawl_args = spider.CLICrawlArgs(XEExchangeRatesSpider)
    crawler = spider.SpiderCrawler(XEExchangeRatesSpider)
    crawl_result = crawler.crawl(*crawl_args)
    print(json.dumps(crawl_result))
    sys.exit(1 if crawl_result.status_code else 0)
