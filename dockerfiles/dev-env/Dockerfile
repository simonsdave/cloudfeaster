ARG CIRCLE_CI_EXECUTOR

FROM $CIRCLE_CI_EXECUTOR

LABEL maintainer="Dave Simons"

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y

COPY install-chrome.sh /tmp/install-chrome.sh
RUN /tmp/install-chrome.sh --chrome
COPY install-chromedriver.sh /tmp/install-chromedriver.sh
RUN /tmp/install-chromedriver.sh

COPY cloudfeaster.tar.gz /tmp/cloudfeaster.tar.gz
RUN python3.9 -m pip install /tmp/cloudfeaster.tar.gz
RUN chmod a+x "$(python3.9 -c 'import cloudfeaster.samples, os; print(os.path.dirname(cloudfeaster.samples.__file__))')/"*.py
RUN rm -rf /tmp/cloudfeaster.tar.gz

ENV DEBIAN_FRONTEND newt
