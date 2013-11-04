#!/usr/bin/env python

import os
import sys
import uuid

import clf.spider
from clf.webdriver_spider import Spider

class MySpider(Spider):

    def crawl(self, browser):

        username_element = browser.find_element_by_xpath("//input[@name='user']")
        username_element.send_keys("dave")

        submit_button = browser.find_element_by_xpath("//input[@value='Submit']")
        submit_button.click()

        balance_locator = "//span[@id='43']"
        login_status = browser.wait_for_login_to_complete(balance_locator)
        if login_status:
            return login_status

        balance_element = browser.find_element_by_xpath(balance_locator)
        balance = balance_element.get_int()

        rv = clf.spider.CrawlResponse(
            clf.spider.SC_OK,
            {
                'balance': balance,
            }
        )
        return rv


if __name__ == "__main__":

    if 2 != len(sys.argv):
        filename = os.path.split(sys.argv[0])[1]
        sys.exit('usage: %s <url>' % filename)

    spider = MySpider(sys.argv[1])
    result = spider.walk()
    print result
