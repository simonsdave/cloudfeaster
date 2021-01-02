ARG PYTHON_VERSION=3.7
ARG ALPINE_VERSION=3.12

FROM python:$PYTHON_VERSION-alpine$ALPINE_VERSION

LABEL maintainer="Dave Simons"

RUN apk add chromium chromium-chromedriver

COPY cloudfeaster.tar.gz /tmp/cloudfeaster.tar.gz
RUN pip install /tmp/cloudfeaster.tar.gz
RUN chmod a+x "$(python -c 'import cloudfeaster.samples, os; print(os.path.dirname(cloudfeaster.samples.__file__))')/"*.py
RUN rm -rf /tmp/cloudfeaster.tar.gz
