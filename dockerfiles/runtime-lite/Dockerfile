FROM python:3.7-alpine

LABEL maintainer="Dave Simons"

RUN echo "http://dl-4.alpinelinux.org/alpine/v3.8/main" >> /etc/apk/repositories
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.8/community" >> /etc/apk/repositories
RUN apk update
RUN apk add chromium chromium-chromedriver
RUN pip install --upgrade pip

COPY cloudfeaster.tar.gz /tmp/cloudfeaster.tar.gz
RUN python3.7 -m pip install /tmp/cloudfeaster.tar.gz
RUN chmod a+x "$(python3.7 -c 'import cloudfeaster.samples, os; print(os.path.dirname(cloudfeaster.samples.__file__))')/"*.py
RUN rm -rf /tmp/cloudfeaster.tar.gz
