import re
import time
import logging

from selenium import webdriver
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

        rv = None
        try:
            browser = Browser()
            browser.get(self.url)
            rv = spider.Spider.walk(self, browser, *args)
            assert isinstance(rv, spider.CrawlResponse)
            browser.quit()
        except Exception as ex:
            rv = spider.CrawlResponse(
                spider.SC_WALK_THREW_EXCEPTION,
                status=str(ex)
            )

        return rv


class Browser(webdriver.Chrome):

    def create_web_element(self, element_id):
        return WebElement(self, element_id)

    def is_element_present(self, xPathLocator):
        try:
            webdriver.Chrome.find_element_by_xpath(
                self,
                xPathLocator )
            return True
        except selenium.common.exceptions.NoSuchElementException:
            pass
        return False

    def _wait_for_element_present_and_displayed(
        self,
        xPathLocator,
        numSecsUntilTimeout=30):
        """..."""
        oneSecond = 1
        while 0 < numSecsUntilTimeout:
            if self.is_element_present( xPathLocator ):
                element = webdriver.Chrome.find_element_by_xpath( self, xPathLocator )
                if element.is_displayed():
                    return True
            numSecsUntilTimeout -= 1
            time.sleep( oneSecond )
        return False

    def find_element_by_xpath(self, xPathLocator):
        """..."""
        self._wait_for_element_present_and_displayed(xPathLocator)
        return webdriver.Chrome.find_element_by_xpath(self, xPathLocator)

    def wait_for_login_to_complete(
        self,
        okXPathLocator,
        badCredentialsXPathLocator=None,
        accountLockedOutXPathLocator=None,
        alertDisplayedIndicatesBadCredentials=None):
        """..."""
        numberSecondsUntilTimeout = 30
        _logger.info(
            "Waiting %d seconds for login to complete",
            numberSecondsUntilTimeout )
        while 0 < numberSecondsUntilTimeout:
            if badCredentialsXPathLocator:
                if self.is_element_present(badCredentialsXPathLocator):
                    rv = spider.CrawlResponse(spider.SC_BAD_CREDENTIALS)
                    return rv

            if alertDisplayedIndicatesBadCredentials:
                if alertDisplayedIndicatesBadCredentials:
                    if self._is_alert_dialog_displayed():
                        rv = spider.CrawlResponse(spider.SC_BAD_CREDENTIALS)
                        return rv

            if accountLockedOutXPathLocator:
                if self.is_element_present(accountLockedOutXPathLocator):
                    rv = spider.CrawlResponse(spider.SC_ACCOUNT_LOCKED_OUT)
                    return rv

            if self.is_element_present(okXPathLocator):
                return None

            oneSecond = 1
            time.sleep(oneSecond)

            numberSecondsUntilTimeout -= 1

            _logger.info(
                "Waiting %d more seconds for login to complete",
                numberSecondsUntilTimeout)

        rv = spider.CrawlResponse(spider.SC_COULD_NOT_CONFIRM_LOGIN_STATUS)
        return rv

    def waitForSignInToComplete(
        self,
        okXPathLocator,
        badCredentialsXPathLocator=None,
        accountLockedOutXPathLocator=None,
        alertDisplayedIndicatesBadCredentials=None):
        """..."""
        rv = self.wait_for_login_to_complete(
            okXPathLocator,
            badCredentialsXPathLocator,
            accountLockedOutXPathLocator,
            alertDisplayedIndicatesBadCredentials )
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
        except selenium.common.exceptions.NoAlertPresentException:
            return False
        return True


class WebElement(selenium.webdriver.remote.webelement.WebElement):

    _nonDigitAndNonDigitRegEx = re.compile( '[^\d^\.]' )

    def __init__( self, parent, id ):
        selenium.webdriver.remote.webelement.WebElement.__init__(
            self,
            parent,
            id )

    def get_text( self ):
        return self.text

    def get_text_and_remove( self, removals ):
        text = self.get_text()
        for removal in removals:
            text = text.replace( removal, "" )
        text = text.strip()
        return text

    def get_text_and_remove_commas( self ):
        return self.get_text_and_remove( [','] )

    def _get_number( self, type, regEx ):
        text = self.get_text()
        if text is None:
            return None

        if regEx is not None:
            match = regEx.match( text )
            if match is None:
                return None
            match_groups = match.groups()
            if 1 != len( match_groups ):
                return None
            text = match_groups[0]
                            
        text = self.__class__._nonDigitAndNonDigitRegEx.sub( '', text )
        return type( text )

    def get_int( self, regEx=None ):
        return self._get_number( int, regEx )

    def get_float( self, regEx=None ):
        return self._get_number( float, regEx )

    def get_selected( self ):
        """..."""
        select = selenium.webdriver.support.select.Select( self )
        for option in select.options:
            if option.is_selected():
                return option
        return None

    def select_by_visible_text(self, visible_text):
        """This method is here only to act as a shortcut so that a spider
        author can write a single line of code to select an option in a list
        rather than two lines of code. Perhaps not a huge saving by every
        little bit helps. As an aside, feels like this is the way the 
        select functionality should have been implemented anyway."""
        select = selenium.webdriver.support.select.Select(self)
        select.select_by_visible_text(visible_text)
