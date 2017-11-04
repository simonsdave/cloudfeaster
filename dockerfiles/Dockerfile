# to build the image
#
#   docker build -t simonsdave/cloudfeaster .
#
# for testing/debugging
#
#   docker run -i -t simonsdave/cloudfeaster /bin/bash
#
# to push to dockerhub
#
#   docker push simonsdave/cloudfeaster
#

FROM ubuntu:14.04

MAINTAINER Dave Simons

RUN apt-get update -y

RUN apt-get install -y curl
RUN curl https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update
RUN apt-get install -y google-chrome-stable

RUN apt-get install -y xvfb

RUN apt-get install -y unzip
RUN curl -s --output chromedriver.zip http://chromedriver.storage.googleapis.com/2.33/chromedriver_linux64.zip
RUN unzip chromedriver.zip
RUN rm chromedriver.zip
RUN mv chromedriver /usr/bin/.
RUN chown root.root /usr/bin/chromedriver
RUN chmod a+wrx /usr/bin/chromedriver

RUN apt-get install -y python
RUN apt-get install -y python-dev
# installing python-crypto, libcurl4-openssl-dev and libffi-dev all seem to
# be required in order to "pip install ndg-httpsclient" without error
RUN apt-get install -y \
    python-crypto \
    libcurl4-openssl-dev \
    libffi-dev
RUN apt-get install -y python-pip
RUN pip install pip==1.5.6

COPY cloudfeaster.tar.gz /tmp/cloudfeaster.tar.gz

#
# pip & setuptools install is here to fix the problem
# introduced with setuptools v34 and described well
# in this bug
#
#   https://github.com/pypa/setuptools/issues/942
# 
RUN pip install -U pip
RUN pip install setuptools==33.1.1

RUN pip install /tmp/cloudfeaster.tar.gz

RUN rm -rf /tmp/cloudfeaster.tar.gz
