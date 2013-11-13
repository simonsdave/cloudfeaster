#!/usr/bin/env bash

# unzip is generally useful
apt-get install unzip

# http://infiniteundo.com/post/54014422873/headless-selenium-testing-with-firefox-and-xvfb

sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list'
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
apt-get update
apt-get -y install google-chrome-stable
# "google-chrome --version" to get "Google Chrome 30.0.1599.66"

# http://damien.co/resources/how-to-install-chromedriver-mac-os-x-selenium-python-7406
# http://chromedriver.storage.googleapis.com/index.html?path=2.4/
# https://code.google.com/p/selenium/wiki/ChromeDriver
cd /tmp
wget http://chromedriver.storage.googleapis.com/2.6/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod a+rx chromedriver
mv chromedriver /usr/bin/.

# Xvfb enables chrome to run in a headless environment
apt-get install -y xvfb

# basic development tools
apt-get install -y vim
echo "set ruler" > ~vagrant/.vimrc
echo "set hlsearch" >> ~vagrant/.vimrc
echo "filetype plugin on" >> ~vagrant/.vimrc
echo "set ts=4" >> ~vagrant/.vimrc
echo "set sw=4" >> ~vagrant/.vimrc
echo "set expandtab" >> ~vagrant/.vimrc
echo "set encoding=UTF8" >> ~vagrant/.vimrc
echo ":syntax enable" >> ~vagrant/.vimrc
echo "autocmd Filetype python setlocal expandtab tabstop=4 shiftwidth=4" >> ~vagrant/.vimrc
chown vagrant.vagrant ~vagrant/.vimrc

# Install and configure git.
# This shell script is run as root user but we'll be logging into
# the provisioned VM as vagrant user.
# "git config" commands are run as root and update root's .gitconfig
# and hence the reason for the mv and chown @ end of this section.
# See http://git-scm.com/book/en/Customizing-Git-Git-Configuration
apt-get install -y git
git config --global core.editor "vi"
git config --global user.name "Dave Simons"
git config --global user.email "simonsdave@gmail.com"
# Tell git to cache github credentials for 1 day (24*60*60=86400).
# See https://help.github.com/articles/set-up-git#platform-linux
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=86400'
mv ~/.gitconfig ~vagrant/.gitconfig
chown vagrant.vagrant ~root/.gitconfig

apt-get install -y python-pip
apt-get install -y python-virtualenv

# 'cause Dave is very set in his old ways ..
echo "PS1=\">\"" >> ~vagrant/.profile
echo "alias dir=\"ls -l\"" >> ~vagrant/.profile
echo "alias cls=clear" >> ~vagrant/.profile
