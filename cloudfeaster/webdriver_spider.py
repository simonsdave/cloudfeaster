"""This module builds on :py:mod:`spider` to introduce the ability
to create `webdriver <http://www.seleniumhq.org/projects/webdriver/>`_
based spiders.
"""

import logging
import os
import re
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.chrome.options import Options
import selenium.webdriver.support.select

import spider

_logger = logging.getLogger(__name__)

# making calls to time.sleep() easier to understand
_quarter_of_a_second = 0.25

# making calls to time.sleep() easier to understand
_half_a_second = 0.5

# making calls to time.sleep() easier to understand
_one_second = 1

# these next 2 variables define the proxy through which the
# spider's traffic is optionally routed
proxy_host = None
proxy_port = None


def _get_chrome_options(user_agent):
    """Take a look @ the README.md in the chrome_proxy_extension
    subdirectory for how this need for creating an on the fly
    chrome extension came about.
    """
    chrome_options = Options()

    chrome = os.environ.get('CLF_CHROME', None)
    if chrome:
        chrome_options.binary_location = chrome

    if os.environ.get('CLF_DISABLE_DEV_SHM_USAGE', None):
        chrome_options.add_argument('--disable-dev-shm-usage')

    if os.environ.get('CLF_NO_SANDBOX', None):
        chrome_options.add_argument('--no-sandbox')

    # https://www.google.com/googlebooks/chrome/med_26.html
    chrome_options.set_headless()

    # :TODO: should the window size be hard-coded? set through environment variable?
    chrome_options.add_argument('window-size=1280x1024')

    if user_agent:
        _logger.info('using user agent >>>%s<<<', user_agent)
        chrome_options.add_argument('user-agent=%s' % user_agent)

    if proxy_host is not None and proxy_port is not None:
        _logger.info('using proxy >>>%s:%d<<<', proxy_host, proxy_port)
        chrome_options.add_argument('--proxy-server=%s:%d' % (proxy_host, proxy_port))

    return chrome_options


class Spider(spider.Spider):
    """This class is an abstract base class for all webdriver spiders."""

    def get_browser(self, url=None, user_agent=None):
        """export CLF_REMOTE_CHROMEDRIVER=http://host.docker.internal:9515"""
        remote_chromedriver = os.environ.get('CLF_REMOTE_CHROMEDRIVER', None)
        return RemoteBrowser(remote_chromedriver, url, user_agent) if remote_chromedriver else Browser(url, user_agent)


class RemoteBrowser(webdriver.Remote):

    def __init__(self, remote_chromedriver, url=None, user_agent=None):
        webdriver.Remote.__init__(self, remote_chromedriver)
        self._url = url

    def __enter__(self):
        """Along with ```___exit___()``` implements the standard
        context manager pattern which, if a none-None url was
        supplied in the ```Browser```'s ctr,
        directs the browser to the specified url when entering
        the context and closes the browser when exiting the
        context. The pattern just makes using
        ```Browser``` way, way cleaner.
        """
        if self._url:
            self.get(self._url)
        return self

    def __exit__(self, exec_type, exec_val, ex_tb):
        """See ```___enter___()```."""
        self.quit()

    def create_web_element(self, element_id):
        """Override the default implementation of
        ```webdriver.Chrome.create_web_element```
        to return a ```WebElement``` instead of a
        ```selenium.webdriver.remote.webelement.WebElement```.
        """
        return WebElement(self, element_id)


class Browser(webdriver.Chrome):
    """This class extends ```webdriver.Chrome``` to add new functionality
    and override existing functionality that is well suited to writing
    webdriver based Spiders.

    :py:meth:`cloudfeaster.Spider.walk` creates an instance of
    :py:class:`Browser` and passes it to the spider's
    :py:meth:`cloudfeaster.Spider.crawl`."""

    def __init__(self, url=None, user_agent=None):
        """Create a new instance of :py:class:`Browser`.

        See :py:meth:`Browser.___enter___` to understand how and when the
        ```url``` argument is used.
        """
        webdriver.Chrome.__init__(self, chrome_options=_get_chrome_options(user_agent))
        self._url = url

    def __enter__(self):
        """Along with ```___exit___()``` implements the standard
        context manager pattern which, if a none-None url was
        supplied in the ```Browser```'s ctr,
        directs the browser to the specified url when entering
        the context and closes the browser when exiting the
        context. The pattern just makes using
        ```Browser``` way, way cleaner.
        """
        if self._url:
            self.get(self._url)
        return self

    def __exit__(self, exec_type, exec_val, ex_tb):
        """See ```___enter___()```."""
        self.quit()

    def create_web_element(self, element_id):
        """Override the default implementation of
        ```webdriver.Chrome.create_web_element```
        to return a :py:class:`WebElement` instead of a
        ```selenium.webdriver.remote.webelement.WebElement```.
        """
        return WebElement(self, element_id)

    def wait_for_login_to_complete(self,
                                   ok_xpath_locator,
                                   bad_credentials_xpath_locator=None,
                                   account_locked_out_xpath_locator=None,
                                   alert_displayed_indicates_bad_credentials=False,
                                   number_seconds_until_timeout=30):

        for i in range(0, number_seconds_until_timeout):
            if self._find_element_by_xpath(ok_xpath_locator):
                return None

            if bad_credentials_xpath_locator:
                if self._find_element_by_xpath(bad_credentials_xpath_locator):
                    return spider.CrawlResponseBadCredentials()

            if alert_displayed_indicates_bad_credentials:
                if self._is_alert_dialog_displayed():
                    return spider.CrawlResponseBadCredentials()

            if account_locked_out_xpath_locator:
                if self._find_element_by_xpath(account_locked_out_xpath_locator):
                    return spider.CrawlResponseAccountLockedOut()

            time.sleep(_one_second)

        return spider.CrawlResponseCouldNotConfirmLoginStatus()

    def wait_for_signin_to_complete(self,
                                    ok_xpath_locator,
                                    bad_credentials_xpath_locator=None,
                                    account_locked_out_xpath_locator=None,
                                    alert_displayed_indicates_bad_credentials=None,
                                    number_seconds_until_timeout=30):
        """This method is just another name for
        :py:meth:`wait_for_login_to_complete` so that spider authors
        can use "login" or "signin" terminology to match
        the semantics of the web site being crawled.
        """
        rv = self.wait_for_login_to_complete(
            ok_xpath_locator,
            bad_credentials_xpath_locator,
            account_locked_out_xpath_locator,
            alert_displayed_indicates_bad_credentials,
            number_seconds_until_timeout)
        return rv

    def _find_element_by_xpath(self, xpath_locator):
        """Private method."""
        try:
            self.find_element_by_xpath(xpath_locator)
        except NoSuchElementException:
            return False
        except UnexpectedAlertPresentException:
            return False

        return True

    def _is_alert_dialog_displayed(self):
        """Private method. Only to be used by CLF infrastructure.
        Couldn't find a good way to test if a JavaScript alert
        dialog was displayed and hence the creation of this
        method. A word of warning. Don't like the implementation
        of this method because it calls switch_to_alert() which
        will (surprise, surprise) switch focus to the alert dialog
        if the dialog is displayed which is almost certainly not
        the desired behaviour. Because of this side effect it's
        probably only wise to use this method when precense of
        alert dialog indicates an error and your spider will be
        terminated if the alert is displayed.
        """
        try:
            alert = self.switch_to_alert()
            alert.text
        except NoAlertPresentException:
            return False

        return True


class WebElement(selenium.webdriver.remote.webelement.WebElement):
    """This class extends
    ```selenium.webdriver.remote.webelement.WebElement```
    to add new functionality and override existing functionality
    that is well suited to writing webdriver based Spiders."""

    _nonDigitAndNonDigitRegEx = re.compile(r'[^\d^\.]')

    def get_text(self):
        """This method exists so spider code can access element data
        using a set of methods instead of a text property and some
        other methods like ```get_int()``` and ```get_float()```.
        """
        return self.text

    def _get_number(self, number_type, reg_ex):
        text = self.get_text()

        if reg_ex:
            match = reg_ex.match(text)
            if match is None:
                return None
            match_groups = match.groups()
            if 1 != len(match_groups):
                return None
            text = match_groups[0]

        text = type(self)._nonDigitAndNonDigitRegEx.sub('', text)
        return number_type(text)

    def get_int(self, reg_ex=None):
        return self._get_number(int, reg_ex)

    def get_float(self, reg_ex=None):
        return self._get_number(float, reg_ex)

    def get_selected(self):
        """This method is here only to act as a shortcut so that a spider
        author can write a single line of code to get the correctly selected
        option in a list rather than the few lines of code that's seen
        in this method's implementation.

        If an option is selected the option's text is returned otherwise
        None is returned.
        """
        select = selenium.webdriver.support.select.Select(self)
        try:
            return select.first_selected_option
        except NoSuchElementException:
            return None

    def select_by_visible_text(self, visible_text):
        """This method is here only to act as a shortcut so that a spider
        author can write a single line of code to select an option in a list
        rather than two lines of code. Perhaps not a huge saving by every
        little bit helps. As an aside, feels like this is the way the
        select functionality should have been implemented anyway.
        """
        select = selenium.webdriver.support.select.Select(self)
        select.select_by_visible_text(visible_text)
