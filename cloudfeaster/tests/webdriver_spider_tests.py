"""This module contains unit tests for the ```webdriver_spider``` module."""

import BaseHTTPServer
import re
import SimpleHTTPServer
import threading
import time
import unittest
import uuid

import mock
from nose.plugins.attrib import attr
import selenium

from .. import spider
from .. import webdriver_spider


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
        httpdAddress = ("127.0.0.1", 0)
        httpd = BaseHTTPServer.HTTPServer(
            httpdAddress,
            HTTPRequestHandler)
        self.portNumber = httpd.server_port
        httpd.serve_forever()
        "never returns"

    def start(self):
        threading.Thread.start(self)
        "give the HTTP server time to start & initialize itself"
        while 'portNumber' not in self.__dict__:
            time.sleep(1)


class ProxyConfigPatcher(object):

    def __init__(self, proxy_host, proxy_port):
        object.__init__(self)

        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

        self.saved_proxy_host = None
        self.saved_proxy_port = None

    def __enter__(self):
        self.saved_proxy_host = webdriver_spider.proxy_host
        self.saved_proxy_port = webdriver_spider.proxy_port

        webdriver_spider.proxy_host = self.proxy_host
        webdriver_spider.proxy_port = self.proxy_port

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        webdriver_spider.proxy_host = self.saved_proxy_host
        webdriver_spider.proxy_port = self.saved_proxy_port


@attr('integration')
class TestBrowser(unittest.TestCase):
    """A series of unit tests that validate ```webdriver_spider.Browser```."""

    @classmethod
    def setUpClass(cls):
        cls._http_server = HTTPServer()
        cls._http_server.start()

    @classmethod
    def tearDownClass(cls):
        cls._http_server = None

    @attr('quick')
    def test_browser_ctr_with_none_url(self):
        with webdriver_spider.Browser(None):
            pass

    @attr('quick')
    @unittest.skip('figure out why travis builds stalling')
    def test_browser_no_proxy(self):
        locator = '//*[@id="proxy-view-effective-settings"]'

        proxy_host = None
        proxy_port = None
        with ProxyConfigPatcher(proxy_host, proxy_port):
            with webdriver_spider.Browser('chrome://net-internals/#proxy') as browser:
                element = browser.find_element_by_xpath(locator)
                text = element.get_text()
                self.assertTrue(text.startswith('Use DIRECT connections.\nSource: SYSTEM'))

    @attr('quick')
    @unittest.skip('figure out why travis builds stalling')
    def test_browser_with_proxy(self):
        locator = '//*[@id="proxy-view-effective-settings"]'

        proxy_host = 'dave'
        proxy_port = 8010
        with ProxyConfigPatcher(proxy_host, proxy_port):
            with webdriver_spider.Browser('chrome://net-internals/#proxy') as browser:
                element = browser.find_element_by_xpath(locator)
                self.assertEqual(
                    'Proxy server: %s:%d' % (proxy_host, proxy_port),
                    element.get_text())

    @attr('quick')
    def test_setting_user_agent(self):
        default_user_agent = 'this will get replaced'

        html = (
            '<html>'
            '<head>'
            '<script type="text/javascript">'
            'function changeUserAgentHeader() {'
            '    document.getElementById("42").innerHTML = navigator.userAgent;'
            '}'
            '</script>'
            '</head>'
            '<body>'
            '<p id=42>%s</p>'
            '<input'
            '   id=43'
            '   type="checkbox"'
            '   onclick="changeUserAgentHeader()">Hi</input>'
            '</body>'
            '</html>'
        ) % default_user_agent

        page = 'testSettingUserAgent.html'
        HTTPServer.html_pages[page] = html
        url = 'http://127.0.0.1:%d/%s' % (
            type(self)._http_server.portNumber,
            page
        )

        user_agent = "dave was here!!!"
        self.assertNotEqual(user_agent, default_user_agent)
        with webdriver_spider.Browser(url, user_agent) as browser:
            paragraph_element = browser.find_element_by_xpath("//p[@id='42']")
            self.assertEqual(paragraph_element.get_text(), default_user_agent)
            button_element = browser.find_element_by_xpath("//input[@id='43']")
            button_element.click()
            self.assertEqual(paragraph_element.get_text(), user_agent)

    @attr('quick')
    def test_is_element_present(self):
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
            type(self)._http_server.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            # Browser ctr does get() on url which
            # only returns after onload event is fired
            self.assertTrue(browser.is_element_present("//h1[@id='42']"))
            self.assertFalse(browser.is_element_present("//h1[@id='43']"))

    @attr('quick')
    def test_find_element_by_xpath_all_good(self):
        html = (
            '<html>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<h1 id=42>Dave Was Here!!!</h1>'
            '</body>'
            '</html>'
        )
        page = "testFindElementByXPathAllGood.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            xpath = "//h1[@id='42']"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)

    @attr('quick')
    def test_find_element_by_xpath_fails_on_invisible_element(self):
        html = (
            '<html>'
            '<head>'
            '<style>'
            'h1 { visibility:hidden; }'
            '</style>'
            '</head>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<h1 id=42>Dave Was Here!!!</h1>'
            '</body>'
            '</html>'
        )
        page = "testFindElementByXPathFailsOnInvisibleElement.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            with self.assertRaises(selenium.common.exceptions.NoSuchElementException):
                xpath = "//h1[@id='42']"
                self.assertTrue(browser.is_element_present(xpath))
                browser.find_element_by_xpath(xpath, num_secs_until_timeout=3)

    @attr('quick')
    def test_find_element_by_xpath_fails_on_missing_element(self):
        html = (
            '<html>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '</body>'
            '</html>'
        )
        page = "testFindElementByXPathFailsOnMissingElement.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            with self.assertRaises(selenium.common.exceptions.NoSuchElementException):
                xpath = "//h1[@id='43']"
                self.assertFalse(browser.is_element_present(xpath))
                browser.find_element_by_xpath(xpath, num_secs_until_timeout=5)

    @attr('quick')
    def test_find_elements_by_xpath_all_good(self):
        html = (
            '<html>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<ol>'
            '<li>Coffee</li>'
            '<li>Tea</li>'
            '<li>Milk</li>'
            '</ol>'
            '</body>'
            '</html>'
        )
        page = "testFindElementsByXPathAllGood.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            xpath = "//ol/li"
            elements = browser.find_elements_by_xpath(xpath)
            self.assertIsNotNone(elements)
            self.assertEqual(3, len(elements))

    @attr('slow')
    def test_find_elements_by_xpath_elements_not_found(self):
        html = (
            '<html>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<ul>'
            '<li>Coffee</li>'
            '<li>Tea</li>'
            '<li>Milk</li>'
            '</ul>'
            '</body>'
            '</html>'
        )
        page = "testFindElementsByXPathElementsNotFound.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            xpath = "//ol/li"
            elements = browser.find_elements_by_xpath(xpath)
            self.assertIsNotNone(elements)
            self.assertEqual(0, len(elements))

    @attr('quick')
    def test_wait_for_login_to_complete_all_good(self):
        html = (
            '<html>'
            '<head>'
            '<script type="text/javascript">'
            'function changeElementId() {'
            '    var element = document.getElementById("42");'
            '    element.setAttribute("id", "43");'
            '}'
            '</script>'
            '</head>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<input'
            '   id=42'
            '   type="checkbox"'
            '   onclick="setTimeout(\'changeElementId()\',1000)">Hi</input>'
            '</body>'
            '</html>'
        )

        page = "testWaitForLoginToCompleteAllGood.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )

        with webdriver_spider.Browser(url) as browser:
            original_element_xpath_locattor = "//input[@id='42']"
            element = browser.find_element_by_xpath(original_element_xpath_locattor)
            self.assertIsNotNone(element)
            self.assertTrue(type(element), webdriver_spider.WebElement)
            element.click()

            ok_xpath_locattor = "//input[@id='43']"
            login_success = browser.wait_for_login_to_complete(ok_xpath_locattor)
            self.assertIsNone(login_success)

    @attr('quick')
    def test_wait_for_login_to_complete_bad_creds(self):
        html = (
            '<html>'
            '<head>'
            '<script type="text/javascript">'
            'function changeElementId() {'
            '    var element = document.getElementById("42");'
            '    element.setAttribute("id", "44");'
            '}'
            '</script>'
            '</head>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<input'
            '   id=42'
            '   type="checkbox"'
            '   onclick="setTimeout(\'changeElementId()\',1000)">Hi</input>'
            '</body>'
            '</html>'
        )

        page = "testWaitForLoginToCompleteBadCreds.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )

        with webdriver_spider.Browser(url) as browser:
            original_element_xpath_locattor = "//input[@id='42']"
            element = browser.find_element_by_xpath(original_element_xpath_locattor)
            self.assertIsNotNone(element)
            self.assertTrue(type(element), webdriver_spider.WebElement)
            element.click()

            ok_xpath_locattor = "//input[@id='43']"
            bad_creds_xpath_locator = "//input[@id='44']"
            login_success = browser.wait_for_login_to_complete(
                ok_xpath_locattor,
                bad_creds_xpath_locator)
            self.assertIsNotNone(login_success)
            self.assertEqual(
                login_success._status_code,
                spider.CrawlResponse.SC_BAD_CREDENTIALS)

    @attr('quick')
    def test_wait_for_login_to_complete_bad_creds_on_alert(self):
        html = (
            '<html>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<input'
            '   id=42'
            '   type="checkbox"'
            '   onclick="setTimeout(\'alert()\',1000)">Hi</input>'
            '</body>'
            '</html>'
        )

        page = "testWaitForLoginToCompleteBadCredsOnAlert.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )

        with webdriver_spider.Browser(url) as browser:
            original_element_xpath_locattor = "//input[@id='42']"
            element = browser.find_element_by_xpath(original_element_xpath_locattor)
            self.assertIsNotNone(element)
            self.assertTrue(type(element), webdriver_spider.WebElement)
            element.click()

            ok_xpath_locattor = "//input[@id='43']"
            bad_creds_xpath_locator = "//input[@id='44']"
            login_success = browser.wait_for_login_to_complete(
                ok_xpath_locattor,
                bad_creds_xpath_locator,
                alert_displayed_indicates_bad_credentials=True)
            self.assertIsNotNone(login_success)
            self.assertEqual(
                login_success._status_code,
                spider.CrawlResponse.SC_BAD_CREDENTIALS)

    @attr('quick')
    def test_wait_for_login_to_complete_account_locked_out(self):
        html = (
            '<html>'
            '<head>'
            '<script type="text/javascript">'
            'function changeElementId() {'
            '    var element = document.getElementById("42");'
            '    element.setAttribute("id", "45");'
            '}'
            '</script>'
            '</head>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<input'
            '   id=42'
            '   type="checkbox"'
            '   onclick="setTimeout(\'changeElementId()\',1000)">Hi</input>'
            '</body>'
            '</html>'
        )

        page = "testWaitForLoginToCompleteBadCreds.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )

        with webdriver_spider.Browser(url) as browser:
            original_element_xpath_locattor = "//input[@id='42']"
            element = browser.find_element_by_xpath(original_element_xpath_locattor)
            self.assertIsNotNone(element)
            self.assertTrue(type(element), webdriver_spider.WebElement)
            element.click()

            ok_xpath_locattor = "//input[@id='43']"
            bad_creds_xpath_locator = "//input[@id='44']"
            account_locked_out_xpath_locator = "//input[@id='45']"
            login_success = browser.wait_for_login_to_complete(
                ok_xpath_locattor,
                bad_creds_xpath_locator,
                account_locked_out_xpath_locator)
            self.assertIsNotNone(login_success)
            self.assertEqual(
                login_success._status_code,
                spider.CrawlResponse.SC_ACCOUNT_LOCKED_OUT)

    @attr('quick')
    def test_wait_for_login_to_complete_could_not_confirm(self):
        html = (
            '<html>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<input id=42 type="checkbox">Hi</input>'
            '</body>'
            '</html>'
        )

        page = "testWaitForLoginToCompleteBadCreds.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )

        with webdriver_spider.Browser(url) as browser:
            original_element_xpath_locattor = "//input[@id='42']"
            element = browser.find_element_by_xpath(original_element_xpath_locattor)
            self.assertIsNotNone(element)
            self.assertTrue(type(element), webdriver_spider.WebElement)
            element.click()

            ok_xpath_locattor = "//input[@id='43']"
            bad_creds_xpath_locator = "//input[@id='44']"
            account_locked_out_xpath_locator = "//input[@id='45']"
            login_success = browser.wait_for_login_to_complete(
                ok_xpath_locattor,
                bad_creds_xpath_locator,
                account_locked_out_xpath_locator,
                number_seconds_until_timeout=3)
            self.assertIsNotNone(login_success)
            self.assertEqual(
                login_success._status_code,
                spider.CrawlResponse.SC_COULD_NOT_CONFIRM_LOGIN_STATUS)

    @attr('quick')
    def test_wait_for_signin_to_complete_is_proxy_for_wait_for_signin_to_complete(self):
        my_ok_xpath_locator = uuid.uuid4()
        my_bad_credentials_xpath_locator = uuid.uuid4()
        my_account_locked_out_xpath_locator = uuid.uuid4()
        my_alert_displayed_indicates_bad_credentials = uuid.uuid4()
        my_number_seconds_until_timeout = uuid.uuid4()
        my_rv = uuid.uuid4()

        def my_patch(self_in_wait_for_login_to_complete_method,
                     ok_xpath_locator,
                     bad_credentials_xpath_locator,
                     account_locked_out_xpath_locator,
                     alert_displayed_indicates_bad_credentials,
                     number_seconds_until_timeout):

            self.assertIsNotNone(self_in_wait_for_login_to_complete_method)
            self.assertEqual(
                type(self_in_wait_for_login_to_complete_method),
                webdriver_spider.Browser)
            self.assertEqual(
                ok_xpath_locator,
                my_ok_xpath_locator)
            self.assertEqual(
                bad_credentials_xpath_locator,
                my_bad_credentials_xpath_locator)
            self.assertEqual(
                account_locked_out_xpath_locator,
                my_account_locked_out_xpath_locator)
            self.assertEqual(
                alert_displayed_indicates_bad_credentials,
                my_alert_displayed_indicates_bad_credentials)
            self.assertEqual(
                number_seconds_until_timeout,
                my_number_seconds_until_timeout)
            return my_rv

        name_of_method_to_patch = "cloudfeaster.webdriver_spider.Browser.wait_for_login_to_complete"
        with mock.patch(name_of_method_to_patch, my_patch):
            with webdriver_spider.Browser() as browser:
                rv = browser.wait_for_signin_to_complete(
                    my_ok_xpath_locator,
                    my_bad_credentials_xpath_locator,
                    my_account_locked_out_xpath_locator,
                    my_alert_displayed_indicates_bad_credentials,
                    my_number_seconds_until_timeout)
                self.assertEqual(rv, my_rv)


@attr('integration')
class TestWebElement(unittest.TestCase):
    """A series of unit tests that validate ```webdriver_spider.WebElement```."""

    @classmethod
    def setUpClass(cls):
        cls._http_server = HTTPServer()
        cls._http_server.start()

    @classmethod
    def tearDownClass(cls):
        cls._http_server = None

    def test_get_text_get_int_and_get_float(self):
        html = (
            '<html>\n'
            '<title>Dave Was Here!!!</title>\n'
            '<body>\n'
            '<h1>42</h1>\n'
            '<h1> 42.43 </h1>\n'
            '<h1> miles 1,342.43 ### </h1>\n'
            '<h1> this\n'
            'is\n'
            '666\n'
            'over many   lines\n'
            'and has 2\n'
            'numbers in one element\n'
            '</h1>\n'
            '</body>\n'
            '</html>'
        )
        page = "testGetTextGetIntAndGetFloat.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            xpath = "//h1[contains(text(),'42')]"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            number = element.get_int()
            self.assertIsNotNone(number)
            self.assertEqual(int, type(number))
            self.assertEqual(42, number)
            number = element.get_float()
            self.assertIsNotNone(number)
            self.assertEqual(float, type(number))
            self.assertEqual(42.0, number)

            xpath = "//h1[contains(text(),'42.43')]"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            number = element.get_float()
            self.assertIsNotNone(number)
            self.assertEqual(float, type(number))
            self.assertEqual(42.43, number)

            xpath = "//h1[contains(text(),'1,342.43')]"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            number = element.get_float()
            self.assertIsNotNone(number)
            self.assertEqual(float, type(number))
            self.assertEqual(1342.43, number)

            xpath = "//h1[contains(text(),'666')]"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            reg_ex = re.compile(
                r".*this\s+is\s+(?P<number>\d+)\s+over.*",
                re.IGNORECASE | re.DOTALL)
            number = element.get_int(reg_ex)
            self.assertIsNotNone(number)
            self.assertEqual(int, type(number))
            self.assertEqual(666, number)

            reg_ex = re.compile(
                r".*and\s+has\s+(?P<number>\d+)\s+numbers.*",
                re.IGNORECASE | re.DOTALL)
            number = element.get_int(reg_ex)
            self.assertIsNotNone(number)
            self.assertEqual(int, type(number))
            self.assertEqual(2, number)

            reg_ex = re.compile(
                r".*this\s+is\s+(?P<one>\d+)\s+over.*and\s+has\s+(?P<two>\d+)\s+numbers.*",
                re.IGNORECASE | re.DOTALL)
            number = element.get_int(reg_ex)
            self.assertIsNone(number)

            reg_ex = re.compile(
                r"NO MATCH HERE (?P<number>\d+)",
                re.IGNORECASE | re.DOTALL)
            number = element.get_int(reg_ex)
            self.assertIsNone(number)

    def test_get_selected_and_select_by_visible_text(self):
        html = (
            '<html>'
            '<head>'
            '<script type="text/javascript">'
            'function deselect_all_options()'
            '{'
            '   document.getElementById("select_element_id").selectedIndex=-1;'
            '}'
            '</script>'
            '</head>'
            '<title>Dave Was Here!!!</title>'
            '<body onload="deselect_all_options()">'
            '<select id="select_element_id">'
            '    <option value="AB" >Alberta</option>'
            '    <option value="BC" >British Columbia</option>'
            '    <option value="MB" >Manitoba</option>'
            '    <option value="NB" >New Brunswick</option>'
            '    <option value="NL" >Newfoundland and Labrador</option>'
            '    <option value="NS" >Nova Scotia</option>'
            '    <option value="ON" >Ontario</option>'
            '    <option value="PE" >Prince Edward Island</option>'
            '    <option value="QC" >Quebec</option>'
            '    <option value="SK" >Saskatchewan</option>'
            '</select>'
            '</body>'
            '</html>'
        )
        page = "testSelectByVisibleTextAndGetSelected.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            xpath = "//select[@id='select_element_id']"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)

            selected_option = element.get_selected()
            self.assertIsNone(selected_option)

            text_to_select = 'Ontario'
            element.select_by_visible_text(text_to_select)

            selected_option = element.get_selected()
            self.assertIsNotNone(selected_option)
            self.assertEqual(selected_option.get_text(), text_to_select)

            with self.assertRaises(selenium.common.exceptions.NoSuchElementException):
                element.select_by_visible_text("some option that won't be in the list")

    def test_get_selected_and_select_by_visible_text_on_non_select_element(self):
        html = (
            '<html>'
            '</head>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<h1 id=42>Dave Was Here!!!</h1>'
            '</body>'
            '</html>'
        )
        page = "testSelectByVisibleTextAndGetSelectedOnNonSelectElement.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            xpath = "//h1[@id='42']"
            element = browser.find_element_by_xpath(xpath)
            self.assertIsNotNone(element)
            with self.assertRaises(selenium.common.exceptions.UnexpectedTagNameException):
                element.get_selected()
            with self.assertRaises(selenium.common.exceptions.UnexpectedTagNameException):
                element.select_by_visible_text("something")

    def test_is_element_present(self):
        html = (
            '<html>'
            '<title>Dave Was Here!!!</title>'
            '<body>'
            '<div>'
            '<h1 id=42>Dave Was Here!!!</h1>'
            '</div>'
            '</body>'
            '</html>'
        )
        page = "testIsElementPresent.html"
        HTTPServer.html_pages[page] = html
        url = "http://127.0.0.1:%d/%s" % (
            type(self)._http_server.portNumber,
            page
        )
        with webdriver_spider.Browser(url) as browser:
            # Browser ctr does get() on url which
            # only returns after onload event is fired
            div = browser.find_element_by_xpath("//div")
            self.assertIsNotNone(div)
            self.assertTrue(div.is_element_present("//h1[@id='42']"))
            self.assertFalse(div.is_element_present("//h1[@id='43']"))
