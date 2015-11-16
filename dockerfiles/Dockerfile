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

FROM simonsdave/cloudfeaster-base

MAINTAINER Dave Simons

COPY cloudfeaster.tar.gz /tmp/cloudfeaster.tar.gz

RUN pip install --process-dependency-links /tmp/cloudfeaster.tar.gz

RUN rm -rf /tmp/cloudfeaster.tar.gz
