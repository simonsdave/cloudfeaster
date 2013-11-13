#!/usr/bin/env bash

# http://infiniteundo.com/post/54014422873/headless-selenium-testing-with-firefox-and-xvfb

sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list'
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
apt-get update
apt-get -y install google-chrome-stable
# "google-chrome --version" to get "Google Chrome 30.0.1599.66"

apt-get install -y git

apt-get install -y python-pip
apt-get install -y python-virtualenv

pip install selenium

apt-get install -y xvfb

apt-get install unzip

# http://damien.co/resources/how-to-install-chromedriver-mac-os-x-selenium-python-7406
# http://chromedriver.storage.googleapis.com/index.html?path=2.6/
# https://code.google.com/p/selenium/wiki/ChromeDriver
cd /tmp
wget http://chromedriver.storage.googleapis.com/2.6/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod a+rx chromedriver
mv chromedriver /usr/bin/.
