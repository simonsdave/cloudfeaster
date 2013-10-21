"""This module contains unit tests for the ```webdriver_spider``` module."""

import BaseHTTPServer
import os
import SimpleHTTPServer
import sys
import threading
import time
import unittest
import uuid

import mock
import selenium

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import spider
import webdriver_spider

class TestSpider(unittest.TestCase):
    """A series of unit tests that validate ```webdriver_spider.Spider```."""

    def test_crawl_args_and_return_value_passed_correctly(self):

        self.my_url = "http://www.example.com"
        self.my_arg1 = str(uuid.uuid4())
        self.my_arg2 = str(uuid.uuid4())
        self.mock_browser = None

        def browser_class_patch(url):
            self.assertEqual(url, self.my_url)
            self.assertIsNone(self.mock_browser)
            self.mock_browser = mock.Mock()
            self.mock_browser.__enter__ = mock.Mock(return_value=self.mock_browser)
            self.mock_browser.__exit__ = mock.Mock(return_value=True)
            return self.mock_browser

        with mock.patch("webdriver_spider.Browser", browser_class_patch):

            self.crawl_rv = spider.CrawlResponse(spider.SC_OK)

            class MySpider(webdriver_spider.Spider):
                def crawl(my_spider_self, browser, arg1, arg2):
                    return self.crawl_rv

            my_spider = MySpider(self.my_url)
            walk_rv = my_spider.walk(self.my_arg1, self.my_arg2)
            self.assertIsNotNone(walk_rv)
            self.assertEqual(walk_rv, self.crawl_rv)

            self.assertIsNotNone(self.mock_browser)
            self.assertEqual(self.mock_browser.__enter__.call_count, 1)
            self.assertEqual(self.mock_browser.__exit__.call_count, 1)




class HTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Only reason this class exists is to stop writing of log messages
    to stdout as part of serving up documents."""

    def log_message(format, *arg):
        """yes this really is meant to be a no-op"""
        pass

    def do_GET(self):
        key = self.path[1:]
        question_mark_index = key.find("?")
        if 0 <= question_mark_index:
            key = key[:question_mark_index]
        html = HTTPServer.html_pages.get(key, "")
        self.send_response(200 if html else 404)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(html))
        self.end_headers()
        self.wfile.write(html)


class HTTPServer(threading.Thread):

    html_pages = {}

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        httpdAddress = ('', 0)
        httpd = BaseHTTPServer.HTTPServer(
            httpdAddress,
            HTTPRequestHandler )
        self.portNumber = httpd.server_port
        httpd.serve_forever()
        "never returns"

    def start(self):
        threading.Thread.start(self)
        "give the HTTP server time to start & initialize itself"
        while 'portNumber' not in self.__dict__:
            time.sleep(1)

class TestBrowser(unittest.TestCase):
    """A series of unit tests that validate ```webdriver_spider.Browser```."""

    @classmethod
    def setUpClass(cls):
        cls._httpServer = HTTPServer()
        cls._httpServer.start()

    @classmethod
    def tearDownClass( cls ):
        cls._httpServer = None

    def test_is_element_present(self):
        """Validate ```webdriver_spider.Browser.is_element_present()```."""
        html = (
            '<html>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<h1 id=42>Dave Was Here!!!</h1>'
            '</body>'
            '</html>'
        )
        page = "testIsElementPresent.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._httpServer.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            enoughTimeForPageToLoad = 5
            time.sleep(enoughTimeForPageToLoad)
            self.assertTrue(browser.is_element_present("//h1[@id='42']"))
            self.assertFalse(browser.is_element_present("//h1[@id='43']"))

    def test_find_element_by_xpath(self):
        """Validate ```webdriver_spider.Browser.find_element_by_xpath()```."""
        html = (
            '<html>'
            '<head>'
            '<script type="text/javascript">'
            'function makeElementVisible()'
            '{'
            'var element = document.getElementById("43");'
            'element.style.visibility="visible";'
            '}'
            'function changeElementId()'
            '{'
            'var element = document.getElementById("42");'
            'element.style.visibility="hidden";'
            'element.setAttribute("id",43);'
            'setTimeout("makeElementVisible()",5000);'
            '}'
            'setTimeout("changeElementId()",5000);'
            '</script>'
            '</head>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<h1 id=42>Dave Was Here!!!</h1>'
            '</body>'
            '</html>'
        )
        page = "testFindElementByXPath.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._httpServer.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            xpath ="//h1[@id='42']"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            self.assertEqual(type(element), webdriver_spider.WebElement)

            xpath ="//h1[@id='43']"
            self.assertFalse(browser.is_element_present(xpath))
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            self.assertEqual(type(element), webdriver_spider.WebElement)

            with self.assertRaises(selenium.common.exceptions.NoSuchElementException):
               xpath ="//h1[@id='42']"
               self.assertFalse(browser.is_element_present(xpath))
               browser.find_element_by_xpath(xpath)

    def _test_wait_for_login_and_signin_to_complete(self, wait_method):
        html = (
            '<html>'
            '<head>'
            '<script type="text/javascript">'
            ''
            'function getQueryStringValue( keyToFind, valueIfKeyNotFound ) {'
            '    keyToFindAsLowerCase = keyToFind.toLowerCase();'
            '    if( document.location.search.length ) {'
            '        queryString = document.location.search.slice( 1 );'
            '        arrayOfKVPs = queryString.split( "&" );'
            '        for (i=0;i<arrayOfKVPs.length;i++) {'
            '            kvp = arrayOfKVPs[i];'
            '            kvpAsArray = kvp.split( "=" );'
            '            key = kvpAsArray[0];'
            '            if( key.toLowerCase() == keyToFindAsLowerCase ) {'
            '                return kvpAsArray[1];'
            '            }'
            '        }'
            '    }'
            '    return valueIfKeyNotFound;'
            '}'
            ''
            'function changeElementId(idToChangeTo)'
            '{'
            '    var element = document.getElementById("42");'
            '    element.setAttribute("id", idToChangeTo);'
            '}'
            ''
            'idToChangeTo = getQueryStringValue("idToChangeTo", "43");'
            'setTimeout("changeElementId(" + idToChangeTo + ")", 5000);'
            ''
            '</script>'
            '</head>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<h1 id=42>Dave Was Here!!!</h1>'
            '</body>'
            '</html>'
        )
        original_element_xpath_locattor = "//h1[@id='42']"
        ok_id = 43
        ok_xpath_locattor = "//h1[@id='%d']" % ok_id
        bad_creds_id = 44
        bad_creds_xpath_locator = "//h1[@id='%d']" % bad_creds_id
        account_locked_out_id = 45
        account_locked_out_xpath_locator = "//h1[@id='%d']" % account_locked_out_id
        never_to_be_found_id = 46

        page = "testWaitForLoginToComplete.html"
        HTTPServer.html_pages[page] = html
        url_fmt = "http://127.0.0.1:%d/%s?idToChangeTo=%%d" % (
            type(self)._httpServer.portNumber,
            page
        )

        with webdriver_spider.Browser(url_fmt % ok_id) as browser:
            # wait for page to load
            element = browser.find_element_by_xpath(original_element_xpath_locattor)
            self.assertIsNotNone(element)
            self.assertTrue(type(element), webdriver_spider.WebElement)

            # post_login_success sb none since this is the success path
            post_login_success = wait_method(
                browser,
                ok_xpath_locattor,
                bad_creds_xpath_locator,
                account_locked_out_xpath_locator)
            self.assertIsNone(post_login_success)

        with webdriver_spider.Browser(url_fmt % ok_id) as browser:
            # wait for page to load
            element = browser.find_element_by_xpath(original_element_xpath_locattor)
            self.assertIsNotNone(element)
            self.assertTrue(type(element), webdriver_spider.WebElement)

            # post_login_success sb none since this is the success path
            post_login_success = wait_method(browser, ok_xpath_locattor)
            self.assertIsNone(post_login_success)

        with webdriver_spider.Browser(url_fmt % account_locked_out_id) as browser:
            # wait for page to load
            element = browser.find_element_by_xpath(original_element_xpath_locattor)
            self.assertIsNotNone(element)
            self.assertTrue(type(element), webdriver_spider.WebElement)

            post_login_success = wait_method(
                browser,
                ok_xpath_locattor,
                bad_creds_xpath_locator,
                account_locked_out_xpath_locator)
            self.assertIsNotNone(post_login_success)
            self.assertEqual(post_login_success.status_code, spider.SC_ACCOUNT_LOCKED_OUT)

        with webdriver_spider.Browser(url_fmt % bad_creds_id) as browser:
            # wait for page to load
            element = browser.find_element_by_xpath(original_element_xpath_locattor)
            self.assertIsNotNone(element)
            self.assertTrue(type(element), webdriver_spider.WebElement)

            post_login_success = wait_method(
                browser,
                ok_xpath_locattor,
                bad_creds_xpath_locator,
                account_locked_out_xpath_locator)
            self.assertIsNotNone(post_login_success)
            self.assertEqual(post_login_success.status_code, spider.SC_BAD_CREDENTIALS)

        with webdriver_spider.Browser(url_fmt % never_to_be_found_id) as browser:
            # wait for page to load
            element = browser.find_element_by_xpath(original_element_xpath_locattor)
            self.assertIsNotNone(element)
            self.assertTrue(type(element), webdriver_spider.WebElement)

            post_login_success = wait_method(
                browser,
                ok_xpath_locattor,
                bad_creds_xpath_locator,
                account_locked_out_xpath_locator)
            self.assertIsNotNone(post_login_success)
            self.assertEqual(
                post_login_success.status_code,
                spider.SC_COULD_NOT_CONFIRM_LOGIN_STATUS)

    def test_wait_for_login_to_complete( self ):
        """Validate ```webdriver_spider.Browser.wait_for_login_and_signin_to_complete()```."""
        self._test_wait_for_login_and_signin_to_complete(
            webdriver_spider.Browser.wait_for_login_to_complete)

    def test_wait_for_signin_to_complete( self ):
        """Validate ```webdriver_spider.Browser.wait_for_login_and_signin_to_complete()```."""
        self._test_wait_for_login_and_signin_to_complete(
            webdriver_spider.Browser.wait_for_signin_to_complete)
