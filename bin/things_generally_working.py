#!/usr/bin/env python

import os
import sys

import time
from selenium import webdriver

if __name__ == "__main__":

    script_name = os.path.split(sys.argv[0])[1]
    if 1 != len(sys.argv):
        sys.exit('usage: %s' % script_name)

    browser = webdriver.Chrome()
    browser.get("https://www.google.com")
    time.sleep(3)
    browser.get_screenshot_as_file('./%s.png' % script_name[:-3])
    browser.quit()
