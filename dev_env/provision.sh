#!/usr/bin/env bash

set -e

apt-get update -y

#
# install docker
#
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-engine
usermod -aG docker vagrant
service docker restart

#
# install and configure git
#
apt-get install -y git

if [ $# == 2 ]; then
    su - vagrant -c "git config --global user.name \"${1:-}\""
    su - vagrant -c "git config --global user.email \"${2:-}\""
fi

su vagrant <<'EOF'
echo 'export VISUAL=vim' >> ~/.profile
echo 'export EDITOR="$VISUAL"' >> ~/.profile
EOF

#
#
#
apt-get install -y python-virtualenv
apt-get install -y python-dev
apt-get build-dep -y python-crypto
apt-get install -y libcurl4-openssl-dev
apt-get install -y libffi-dev
apt-get build-dep -y python-pycurl
apt-get install -y unzip

# see use of pypandoc in setup.py
apt-get install -y pandoc

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

#
# install nginx
#
apt-get install -y nginx
cp /vagrant/nginx.site /etc/nginx/sites-available/default
mkdir -p /usr/share/nginx/cloudfeaster/html
chown root:root /usr/share/nginx/cloudfeaster/html
service nginx restart

#
# jq is just so generally useful
#
JQ_SOURCE=https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64
JQ_BIN=/usr/local/bin/jq
curl -s -L --output "$JQ_BIN" "$JQ_SOURCE"
chown root.root "$JQ_BIN"
chmod a+x "$JQ_BIN"

#
# install latest version of chrome
#
curl https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
apt-get update
apt-get install -y google-chrome-stable

#
# install chromedriver
#
pushd /tmp
CHROMEDRIVER_SOURCE=http://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip
CHROMEDRIVER_ZIP=chromedriver.zip
CHROMEDRIVER_BIN=/usr/local/bin/chromedriver
curl -s --output "$CHROMEDRIVER_ZIP" "$CHROMEDRIVER_SOURCE"
unzip "$CHROMEDRIVER_ZIP"
mv chromedriver "$CHROMEDRIVER_BIN"
chown root.root "$CHROMEDRIVER_BIN"
chmod a+x "$CHROMEDRIVER_BIN"
popd

#
# install xvfb
#
apt-get install -y xvfb

#
# customize vim
#
su vagrant <<'EOF'
echo 'set ruler' > ~/.vimrc
echo 'set hlsearch' >> ~/.vimrc
echo 'filetype plugin on' >> ~/.vimrc
echo 'filetype indent on' >> ~/.vimrc
echo 'set ts=4' >> ~/.vimrc
echo 'set sw=4' >> ~/.vimrc
echo 'set expandtab' >> ~/.vimrc
echo 'set encoding=UTF8' >> ~/.vimrc
echo 'colorscheme koehler' >> ~/.vimrc
echo 'syntax on' >> ~/.vimrc

echo 'au BufNewFile,BufRead *.sh set filetype=shell' >> ~/.vimrc
echo 'autocmd Filetype shell setlocal expandtab tabstop=4 shiftwidth=4' >> ~/.vimrc

echo 'au BufNewFile,BufRead *.json set filetype=json' >> ~/.vimrc
echo 'autocmd FileType json setlocal expandtab tabstop=4 shiftwidth=4' >> ~/.vimrc

echo 'au BufNewFile,BufRead *.py set filetype=python' >> ~/.vimrc
echo 'autocmd FileType python setlocal expandtab tabstop=4 shiftwidth=4' >> ~/.vimrc

echo 'au BufNewFile,BufRead *.raml set filetype=raml' >> ~/.vimrc
echo 'autocmd FileType raml setlocal expandtab tabstop=2 shiftwidth=2' >> ~/.vimrc

echo 'au BufNewFile,BufRead *.yaml set filetype=yaml' >> ~/.vimrc
echo 'autocmd FileType yaml setlocal expandtab tabstop=2 shiftwidth=2' >> ~/.vimrc

echo 'au BufNewFile,BufRead *.js set filetype=javascript' >> ~/.vimrc
echo 'autocmd FileType javascript setlocal expandtab tabstop=2 shiftwidth=2' >> ~/.vimrc

# install pathogen
mkdir -p ~/.vim/autoload ~/.vim/bundle
curl -LSso ~/.vim/autoload/pathogen.vim https://tpo.pe/pathogen.vim
sed -i '1s|^|execute pathogen#infect()\n|' ~/.vimrc
EOF

exit 0
