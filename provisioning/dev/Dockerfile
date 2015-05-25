# docker build -t simonsdave/cloudfeaster_dev .
# docker run -i -t simonsdave/cloudfeaster_dev /bin/bash
# docker push simonsdave/cloudfeaster_dev

FROM ubuntu:14.04

MAINTAINER Dave Simons

RUN apt-get update

RUN apt-get install -y curl
RUN curl https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update
RUN apt-get install -y google-chrome-stable

RUN apt-get install -y xvfb

RUN apt-get install -y unzip
RUN curl -s --output chromedriver.zip http://chromedriver.storage.googleapis.com/2.15/chromedriver_linux64.zip
RUN unzip chromedriver.zip
RUN rm chromedriver.zip
RUN mv chromedriver /usr/bin/.
RUN chown root.root /usr/bin/chromedriver
RUN chmod a+wrx /usr/bin/chromedriver

RUN apt-get install -y git
RUN apt-get install -y python-virtualenv
RUN apt-get install -y python-dev
