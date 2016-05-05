# to build the image
#
#   sudo docker build -t simonsdave/cloudfeaster .
#
# for testing/debugging
#
#   sudo docker run -i -t simonsdave/cloudfeaster /bin/bash
#
# to push to dockerhub
#
#   sudo docker push simonsdave/cloudfeaster
#

FROM ubuntu:14.04

MAINTAINER Dave Simons

RUN apt-get update -y

# was getting "chfn: PAM: System error" messages during install
# and advice from following page was to do the "ln -s"
# http://stackoverflow.com/questions/25193161/chfn-pam-system-error-intermittently-in-docker-hub-builds/25267015#25267015
RUN ln -s -f /bin/true /usr/bin/chfn

RUN apt-get install -y curl
RUN curl https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update
RUN apt-get install -y google-chrome-stable

RUN apt-get install -y xvfb

RUN apt-get install -y unzip
RUN curl -s --output chromedriver.zip http://chromedriver.storage.googleapis.com/2.21/chromedriver_linux64.zip
RUN unzip chromedriver.zip
RUN rm chromedriver.zip
RUN mv chromedriver /usr/bin/.
RUN chown root.root /usr/bin/chromedriver
RUN chmod a+wrx /usr/bin/chromedriver

RUN apt-get install -y python
RUN apt-get install -y python-pip
RUN pip install pip==1.5.6

COPY cloudfeaster.tar.gz /tmp/cloudfeaster.tar.gz

RUN pip install --process-dependency-links /tmp/cloudfeaster.tar.gz

RUN rm -rf /tmp/cloudfeaster.tar.gz
