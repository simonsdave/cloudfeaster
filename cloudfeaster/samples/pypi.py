#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This spider attempts to login to pypi with a username and password
supplied at runtime. This sample is intended to illustrate how to
work with identifying and authenticating factors. The key thing to
focus on with this spider is get_metadata().
"""

import json
import sys

from cloudfeaster import spider
from cloudfeaster import webdriver_spider


class PyPISpider(spider.Spider):

    @classmethod
    def get_metadata(cls):
        return {
            'url': 'https://pypi.python.org/pypi',
            'identifying_factors': {
                'username': {
                    'pattern': '^.+$',
                },
            },
            'authenticating_factors': {
                'password': {
                    'pattern': '^.+$',
                },
            },
            'factor_display_order': [
                'username',
                'password'
            ],
            'factor_display_names': {
                'username': {
                    'en': 'username',
                    'fr': "Nom d'utilisateur",
                    'ja': 'ユーザー名',
                },
                'password': {
                    'en': 'Password',
                    'fr': 'mot de passe',
                    'ja': 'パスワード',
                },
            },
        }

    def crawl(self, username, password):
        with webdriver_spider.Browser(self.url) as browser:
            return self._crawl(browser, username, password)

    def _crawl(self, browser, username, password):
        xpath = '//a[text()="Log in"]'
        login_link_element = browser.find_element_by_xpath(xpath)
        login_link_element.click()

        xpath = '//input[@name="username"]'
        username_input_element = browser.find_element_by_xpath(xpath)
        username_input_element.send_keys(username)

        xpath = '//input[@name="password"]'
        password_input_element = browser.find_element_by_xpath(xpath)
        password_input_element.send_keys(password)

        xpath = '//input[@value="Login"]'
        login_input_element = browser.find_element_by_xpath(xpath)
        login_input_element.click()

        login_successful_xpath = '//a[text()="Logout"]'
        bad_credentials_xpath = '//a[text()="reset for you"]'
        bad_login_crawl_response = browser.wait_for_login_to_complete(
            login_successful_xpath,
            bad_credentials_xpath)
        if bad_login_crawl_response:
            return bad_login_crawl_response

        xpath = '//a[text()="Logout"]'
        logout_link_element = browser.find_element_by_xpath(xpath)
        logout_link_element.click()

        xpath = '//a[text()="Log in"]'
        login_link_element = browser.find_element_by_xpath(xpath)

        return spider.CrawlResponseOk({})


if __name__ == '__main__':
    crawl_args = spider.CLICrawlArgs(PyPISpider)
    crawler = spider.SpiderCrawler(PyPISpider)
    crawl_result = crawler.crawl(*crawl_args)
    print json.dumps(crawl_result)
    sys.exit(1 if crawl_result._status_code else 0)
