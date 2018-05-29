#!/usr/bin/env bash
#
# spiders.sh exists only as a thin wrapper for spiders.py.
#
# What's the point of spiders.sh? Collections of spiders are
# packaged in docker images and Cloudfeaster Services
# exposes a RESTful API that enables discovery and execution
# of spiders packaged in the docker images. Wanted to
# be able to describe the API exposed by a docker image
# containing spiders in a "platform neutral" way. What does
# "platform neutral" mean in this context? Although this
# project advocates for spiders being written using Python
# and Webdriver there may be better approaches for authoring
# some types of spiders while still wanting to use the
# Cloudfeaster Services infrastructure. By creating this
# and other shell script wrappers, the docker images API
# can be described in ways that does not include any
# reference to Python and Webdriver.
#

spiders.py "$@"
exit $?
