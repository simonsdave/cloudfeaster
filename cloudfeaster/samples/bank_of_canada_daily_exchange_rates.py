#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys

from cloudfeaster import spider
from cloudfeaster import webdriver_spider


class BankOfCanadaDailyExchangeRatesSpider(spider.Spider):

    @classmethod
    def get_metadata(cls):
        return {
            'url': 'http://www.bankofcanada.ca/rates/exchange/daily-exchange-rates/',
        }

    def crawl(self):
        with webdriver_spider.Browser(self.url) as browser:
            return self._crawl(browser)

    def _crawl(self, browser):
        data = {
            'rates': {
            }
        }

        for row_element in browser.find_elements_by_xpath('//div[@class="table-responsive"]/table/tbody/tr'):
            if row_element.is_element_present('th'):
                elements = row_element.find_elements_by_xpath('th')
                date = elements[-1].get_text()
                data['rates_on'] = date
            else:
                if row_element.is_element_present('td'):
                    elements = row_element.find_elements_by_xpath('td')
                    currency = elements[0].get_text()
                    fx_rate = elements[-1].get_float()
                    data['rates'][currency] = fx_rate

        return spider.CrawlResponseOk(data)


if __name__ == '__main__':
    crawl_args = spider.CLICrawlArgs(BankOfCanadaDailyExchangeRatesSpider)
    crawler = spider.SpiderCrawler(BankOfCanadaDailyExchangeRatesSpider)
    crawl_result = crawler.crawl(*crawl_args)
    print json.dumps(crawl_result)
    sys.exit(1 if crawl_result._status_code else 0)
