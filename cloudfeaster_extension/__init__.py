"""...
"""

import selenium


def send_keys(webelement, value):
    print "ORIGINAL >>>%s<<<" % value
    selenium.webdriver.remote.webelement.WebElement.send_keys(webelement, value)

def user_agent():
    return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
