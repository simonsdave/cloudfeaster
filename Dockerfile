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
RUN apt-get install -y python
RUN apt-get install -y python-pip
RUN pip install pip==1.5.6

ADD bin bin
ADD cloudfeaster cloudfeaster
ADD setup.py .
ADD MANIFEST.in .

RUN python setup.py sdist --formats=gztar

RUN pip install --process-dependency-links dist/cloudfeaster-*.*.*.tar.gz
