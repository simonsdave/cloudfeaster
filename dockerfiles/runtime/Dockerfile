FROM ubuntu:18.04

LABEL maintainer="Dave Simons"

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y --fix-missing

#
# python 3
# -- inspired by https://websiteforstudents.com/installing-the-latest-python-3-7-on-ubuntu-16-04-18-04/
# -- python versions @ https://www.python.org/downloads/
# -- pip3 inspired by https://linuxize.com/post/how-to-install-pip-on-ubuntu-18.04/
#
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update -y
RUN apt-get install -y python3.7
RUN apt-get install -y python3-pip

# :TODO: install-chrome.sh & install-chromedriver.sh need cURL but
# nothing else should - is there a cleaner way of not having to
# install curl?
RUN apt-get install -y curl

COPY install-chrome.sh /tmp/install-chrome.sh
RUN /tmp/install-chrome.sh
COPY install-chromedriver.sh /tmp/install-chromedriver.sh
RUN /tmp/install-chromedriver.sh

COPY cloudfeaster.tar.gz /tmp/cloudfeaster.tar.gz
RUN python3.7 -m pip install /tmp/cloudfeaster.tar.gz
RUN chmod a+x "$(python3.7 -c 'import cloudfeaster.samples, os; print(os.path.dirname(cloudfeaster.samples.__file__))')/"*.py
RUN rm -rf /tmp/cloudfeaster.tar.gz

RUN adduser headless --system
USER headless

ENV DEBIAN_FRONTEND newt
