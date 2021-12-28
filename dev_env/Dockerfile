ARG CIRCLE_CI_EXECUTOR

FROM $CIRCLE_CI_EXECUTOR

LABEL maintainer="Dave Simons"

ENV DEBIAN_FRONTEND noninteractive

RUN mkdir /tmp/package
ADD package.tar.gz /tmp/package/.

RUN /tmp/package/bin/install-chrome.sh --chrome
RUN /tmp/package/bin/install-chromedriver.sh

RUN awk '{print >out}; /install_requires/{out="/dev/stdout"} /]/{out="/dev/null"}' out=/dev/null /tmp/package/setup.py | sed -e "s|^[[:space:]]*'||g" | sed -e "s|',[[:space:]]*$||g" | head -n -1 > /tmp/requirements.txt
RUN python3.9 -m pip install --requirement /tmp/requirements.txt

RUN rm -rf /tmp/package /tmp/requirements.txt

ENV DEBIAN_FRONTEND newt
