import re
import time
import logging

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import selenium.webdriver.support.select

import spider


_logger = logging.getLogger("CLF_%s" % __name__)


class Spider(spider.Spider):
    """Abstract base class for a WebDriver based spider."""

    def __init__(self, url):
        spider.Spider.__init__(self, url)

    def walk(self, *args):
        """This method is intended for use by the CLF infrastructure.
        Spiders should not use this method directly. Always returns
        ```spider.CrawlResponse``` and won't throw an exception."""

        with Browser(self.url) as browser:
            return spider.Spider.walk(self, browser, *args)


class Browser(webdriver.Chrome):
    """This class extends ```webdriver.Chrome``` to add new functionality
    and override existing functionality that is well suited to writing
    webdriver based Spiders.

    ```Spider.walk()``` creates an instance of
    ```Browser``` and passes it to the spider's crawl
    method.""" 

    def __init__(self, url=None):
        """Creates a new instance of ``webdriver_spider.Browser```.
        See ```___enter___()``` to understand how and when the
        ```url``` argument is used."""
        webdriver.Chrome.__init__(self)
        self._url = url

    def __enter__(self):
        """Along with ```___exit___()``` implements the standard
        context manager pattern which, if a none-None url was
        supplied in the ```Browser```'s ctr,
        directs the browser to the specified url when entering
        the context and closes the browser when exiting the
        context. The pattern just makes using
        ```Browser``` way, way cleaner."""
        if self._url:
            self.get(self._url)
        return self

    def __exit__(self, exec_type, exec_val, ex_tb):
        """See ```___enter___()```."""
        self.quit()

    def create_web_element(self, element_id):
        """Override the default implementation of
        ```webdriver.Chrome.create_web_element```
        to return a ```.WebElement``` instead of a
        ```selenium.webdriver.remote.webelement.WebElement```."""
        return WebElement(self, element_id)

    def is_element_present(self, xpath_locator):
        """Returns ```True``` if there's an element on the current
        page identifid by ```xpath_locator``` otherwise returns
        ```False```."""
        try:
            webdriver.Chrome.find_element_by_xpath(self, xpath_locator)
            return True
        except NoSuchElementException:
            pass
        return False

    def find_element_by_xpath(self, xpath_locator, num_secs_until_timeout=30):
        """Override the base class' implementation of
        ```webdriver.Chrome.find_element_by_xpath```
        to wait for upto 30 seconds until
        ```is_element_present()``` returns ```True```
        and the element's ```is_displayed()``` also
        to return ```True```. Once these conditions
        have been met or 30 seconds has elapsed,
        ```webdriver.Chrome.find_element_by_xpath```
        is called and the return value returned."""
        one_second = 1
        while 0 < num_secs_until_timeout:
            if self.is_element_present(xpath_locator):
                element = webdriver.Chrome.find_element_by_xpath(self, xpath_locator)
                if element.is_displayed():
                    return element
            num_secs_until_timeout -= 1
            time.sleep(one_second)
        ex = NoSuchElementException("no such element")
        raise ex

    def wait_for_login_to_complete(
        self,
        ok_xpath_locator,
        bad_credentials_xpath_locator=None,
        account_locked_out_xpath_locator=None,
        alert_displayed_indicates_bad_credentials=None):
        """..."""
        number_seconds_until_timeout = 30
        _logger.info(
            "Waiting %d seconds for login to complete",
            number_seconds_until_timeout)
        while 0 < number_seconds_until_timeout:
            if bad_credentials_xpath_locator:
                if self.is_element_present(bad_credentials_xpath_locator):
                    return spider.CrawlResponse(spider.SC_BAD_CREDENTIALS)

            if alert_displayed_indicates_bad_credentials:
                if self._is_alert_dialog_displayed():
                    return spider.CrawlResponse(spider.SC_BAD_CREDENTIALS)

            if account_locked_out_xpath_locator:
                if self.is_element_present(account_locked_out_xpath_locator):
                    return spider.CrawlResponse(spider.SC_ACCOUNT_LOCKED_OUT)

            if self.is_element_present(ok_xpath_locator):
                return None

            one_second = 1
            time.sleep(one_second)

            number_seconds_until_timeout -= 1

            _logger.info(
                "Waiting %d more seconds for login to complete",
                number_seconds_until_timeout)

        return spider.CrawlResponse(spider.SC_COULD_NOT_CONFIRM_LOGIN_STATUS)

    def wait_for_signin_to_complete(
        self,
        ok_xpath_locator,
        bad_credentials_xpath_locator=None,
        account_locked_out_xpath_locator=None,
        alert_displayed_indicates_bad_credentials=None):
        """This method is just another name for
        ```wait_for_login_to_complete()```."""
        rv = self.wait_for_login_to_complete(
            ok_xpath_locator,
            bad_credentials_xpath_locator,
            account_locked_out_xpath_locator,
            alert_displayed_indicates_bad_credentials)
        return rv

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
        terminated if the alert is displayed."""
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

    _nonDigitAndNonDigitRegEx = re.compile('[^\d^\.]')

    def get_text(self):
        """This method exists so spider code can access element data
        using a set of methods instead of a text property and some
        other methods like ```get_int()``` and ```get_float()```."""
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
        None is returned."""
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
        select functionality should have been implemented anyway."""
        select = selenium.webdriver.support.select.Select(self)
        select.select_by_visible_text(visible_text)
