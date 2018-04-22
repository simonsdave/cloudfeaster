# to build the image
#
#   docker build -t simonsdave/cloudfeaster .
#
# for testing/debugging
#
#   docker run -i -t simonsdave/cloudfeaster /bin/bash
#   docker run simonsdave/cloudfeaster spiders.py
#   docker run simonsdave/cloudfeaster spiders.py --samples
#   docker run simonsdave/cloudfeaster spiderhost.py cloudfeaster.samples.bank_of_canada_daily_exchange_rates.BankOfCanadaDailyExchangeRatesSpider
#
# to push to dockerhub
#
#   docker push simonsdave/cloudfeaster
#

FROM ubuntu:16.04

MAINTAINER Dave Simons

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y

RUN apt-get install -y curl
RUN curl https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update -y
RUN apt-get install -y google-chrome-stable

RUN apt-get install -y unzip && \
    curl -s --output chromedriver.zip http://chromedriver.storage.googleapis.com/2.38/chromedriver_linux64.zip && \
    unzip chromedriver.zip && \
    rm chromedriver.zip && \
    mv chromedriver /usr/bin/. && \
    chown root.root /usr/bin/chromedriver && \
    chmod a+wrx /usr/bin/chromedriver

RUN apt-get install -y python python-pip && \
    pip install --upgrade pip

# installing python-crypto, libcurl4-openssl-dev and libffi-dev all seem to
# be required in order to successfully run "pip install ndg-httpsclient"
# and pip install of ndg-httpsclient is part of pip installing cloudfeaster
RUN apt-get install -y \
    python-crypto \
    libcurl4-openssl-dev \
    libffi-dev

COPY cloudfeaster.tar.gz /tmp/cloudfeaster.tar.gz

RUN pip install /tmp/cloudfeaster.tar.gz

RUN rm -rf /tmp/cloudfeaster.tar.gz

# chrome has to run as a non-root user otherwise it will fail to start
RUN useradd headless --shell /bin/bash --create-home \
  && usermod -a -G sudo headless \
  && echo 'ALL ALL = (ALL) NOPASSWD: ALL' >> /etc/sudoers \
  && echo 'headless:nopassword' | chpasswd

USER headless

ENV DEBIAN_FRONTEND newt
