#!/usr/bin/env bash

set -e

apt-get update -y

apt-get install -y docker.io
sed -i -e 's|#DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4"|DOCKER_OPTS="-H tcp://172.17.42.1:2375 -H unix:///var/run/docker.sock"|g' /etc/default/docker
service docker restart

apt-get install -y git
apt-get install -y python-virtualenv
apt-get install -y python-dev
apt-get build-dep -y python-crypto
apt-get install -y libcurl4-openssl-dev
apt-get install -y libffi-dev
apt-get build-dep -y python-pycurl
apt-get install -y unzip

timedatectl set-timezone EST

#
# this install process does not feel right
# how come we're not using nvm?
# could not get nvm to work here :-(
#
apt-get install -y nodejs
apt-get install -y npm
ln -s /usr/bin/nodejs /usr/bin/node
chmod a+x /usr/bin/nodejs
curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
apt-get install -y nodejs
npm i -g raml2md
npm i -g raml2html

apt-get install -y nginx
cp /vagrant/nginx.site /etc/nginx/sites-available/default
mkdir -p /usr/share/nginx/cloudfeaster/html
chown root:root /usr/share/nginx/cloudfeaster/html
service nginx restart

curl -s -L --output /etc/jq 'https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64'
chown root.root /etc/jq
chmod a+x /etc/jq

curl https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
apt-get update
apt-get install -y google-chrome-stable

apt-get install -y unzip
curl -s --output chromedriver.zip http://chromedriver.storage.googleapis.com/2.21/chromedriver_linux64.zip
unzip chromedriver.zip
rm chromedriver.zip
mv chromedriver /usr/bin/.
chown root.root /usr/bin/chromedriver
chmod a+wrx /usr/bin/chromedriver

apt-get install -y xvfb

cp /vagrant/.vimrc ~vagrant/.vimrc
chown vagrant:vagrant ~vagrant/.vimrc

echo 'export VISUAL=vim' >> ~vagrant/.profile
echo 'export EDITOR="$VISUAL"' >> ~vagrant/.profile

if [ $# == 2 ]; then
    su - vagrant -c "git config --global user.name \"${1:-}\""
    su - vagrant -c "git config --global user.email \"${2:-}\""
fi

exit 0
