#!/usr/bin/env bash

set -e

apt-get update -y

apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" | tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-engine
usermod -aG docker vagrant
service docker restart

apt-get install -y git

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
# Compile FFmpeg on Ubuntu, Debian, or Mint
# (http://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu)
#

# pre-reqs
apt-get -y install \
    autoconf \
    automake \
    build-essential \
    libass-dev \
    libfreetype6-dev \
    libsdl2-dev \
    libtheora-dev \
    libtool \
    libva-dev \
    libvdpau-dev \
    libvorbis-dev \
    libxcb1-dev \
    libxcb-shm0-dev \
    libxcb-xfixes0-dev \
    pkg-config \
    texinfo \
    zlib1g-dev

# codecs+
apt-get install -y yasm
apt-get install -y libx264-dev
apt-get install -y libmp3lame-dev
apt-get install -y libopus-dev
apt-get install -y libvpx-dev

# what are these for?
# apt-get install -y alsa-utils
# apt-get install -y v4l-utils

# URL from https://www.ffmpeg.org/download.html
pushd /tmp
curl -s --output ffmpeg.tar.bz2 http://ffmpeg.org/releases/ffmpeg-3.2.4.tar.bz2
tar xvf ffmpeg.tar.bz2
cd ffmpeg*

# got "--enable-x11grab" from
# https://lists.ubuntu.com/archives/ubuntu-users/2016-October/288024.html
PATH="$PWD/bin:$PATH" PKG_CONFIG_PATH="$PWD/ffmpeg_build/lib/pkgconfig" ./configure \
  --prefix="$PWD/ffmpeg_build" \
  --pkg-config-flags="--static" \
  --extra-cflags="-I$PWD/ffmpeg_build/include" \
  --extra-ldflags="-L$PWD/ffmpeg_build/lib" \
  --bindir="$PWD/bin" \
  --enable-x11grab \
  --enable-gpl \
  --enable-libass \
  --enable-libfreetype \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libtheora \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-nonfree

PATH="$PWD/bin:$PATH" make
make install
chmod a+x bin/*
cp bin/* /usr/local/bin

popd

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

curl https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
apt-get update
apt-get install -y google-chrome-stable

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
