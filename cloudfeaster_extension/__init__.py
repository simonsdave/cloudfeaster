"""The functions below identify extensibility points that the service infrastructure
may reimplement at crawl time.
"""

import selenium


def send_keys(paranoia_level, webelement, value):
    selenium.webdriver.remote.webelement.WebElement.send_keys(webelement, value)


def user_agent():
    return (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/73.0.3683.86 Safari/537.36'
    )


def proxy(paranoia_level):
    return (None, None)
