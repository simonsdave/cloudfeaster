ARG PYTHON_VERSION=3.7
ARG ALPINE_VERSION=3.12

FROM python:$PYTHON_VERSION-alpine$ALPINE_VERSION

LABEL maintainer="Dave Simons"

RUN apk add curl
RUN apk add unzip

COPY install-chrome.sh /tmp/install-chrome.sh
RUN /tmp/install-chrome.sh --chromium
COPY install-chromedriver.sh /tmp/install-chromedriver.sh
RUN /tmp/install-chromedriver.sh

COPY cloudfeaster.tar.gz /tmp/cloudfeaster.tar.gz
RUN pip install /tmp/cloudfeaster.tar.gz
RUN chmod a+x "$(python -c 'import cloudfeaster.samples, os; print(os.path.dirname(cloudfeaster.samples.__file__))')/"*.py
RUN rm -rf /tmp/cloudfeaster.tar.gz
