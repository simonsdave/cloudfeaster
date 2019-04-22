"""...
"""

import selenium


def send_keys(webelement, value):
    print "ORIGINAL >>>%s<<<" % value
    selenium.webdriver.remote.webelement.WebElement.send_keys(webelement, value)
