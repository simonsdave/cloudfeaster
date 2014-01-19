#!/usr/bin/env bash

apt-get install -y python-pip
apt-get install -y python-setuptools
# cd /tmp
# wget -q - http://python-distribute.org/distribute_setup.py
# python distribute_setup.py
# apt-get install -y python-virtualenv

apt-get install -y unzip

# http://infiniteundo.com/post/54014422873/headless-selenium-testing-with-firefox-and-xvfb
sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list'
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
apt-get update
apt-get install -y google-chrome-stable
# "google-chrome --version" to get "Google Chrome 30.0.1599.66"

# http://damien.co/resources/how-to-install-chromedriver-mac-os-x-selenium-python-7406
# http://chromedriver.storage.googleapis.com/index.html?path=2.6/
# https://code.google.com/p/selenium/wiki/ChromeDriver
cd /tmp
wget http://chromedriver.storage.googleapis.com/2.8/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
chmod a+rx chromedriver
mv chromedriver /usr/bin/.

# install docker
# http://docs.docker.io/en/latest/installation/ubuntulinux/#ubuntu-precise-12-04-lts-64-bit
# apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
# sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"
# apt-get update
# apt-get install -y lxc-docker

# libgmp-dev installed to avoid the warning
#   "warning: GMP or MPIR library not found; Not building Crypto.PublicKey._fastmath."
# when install pycrypto
apt-get install -y libgmp-dev

# installing python-dev was req'd because pycrypto install was failing
# when trying to install clf's setup.py - the article below describes
# the problem and sol'n
# http://stackoverflow.com/questions/11596839/install-pycrypto-on-ubuntu
apt-get install -y python-dev

echo "############################################################"
# :TODO: in future, there should be a spider host specific setup.py
cd /tmp
cp /vagrant/artifacts/clf-*.*.tar.gz .
gunzip clf-*.*.tar.gz
tar xvf clf-*.*.tar
cd clf-*.*
sudo python setup.py install
cd /tmp
rm -rf clf-*.*. >& /dev/null

echo "############################################################"
# setup local user and group to run clf daemons
useradd --system --user-group --create-home clf

echo "############################################################"
# :TODO: should be installed in the clf user
cp /vagrant/artifacts/.boto ~vagrant/.
chown vagrant.vagrant ~vagrant/.boto
chmod a-rwx ~vagrant/.boto
chmod u+r ~vagrant/.boto

echo "############################################################"
apt-get install -y xvfb

echo "############################################################"

