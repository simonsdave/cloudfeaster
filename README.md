#CloudFeaster [![Requirements Status](https://requires.io/github/simonsdave/cloudfeaster/requirements.svg?branch=master)](https://requires.io/github/simonsdave/cloudfeaster/requirements/?branch=master) [![Build Status](https://travis-ci.org/simonsdave/cloudfeaster.svg?branch=master)](https://travis-ci.org/simonsdave/cloudfeaster) [![Coverage Status](https://coveralls.io/repos/simonsdave/cloudfeaster/badge.svg)](https://coveralls.io/r/simonsdave/cloudfeaster)

CloudFeaster is a screen scraping infrastructure that leverages
modern software engineering tools, services and trends to create:

* a spider authoring and maintenance environment
* an IaaS based operational infrastructure for running spiders
via a RESTful API

Read [this](docs/story.md) to understand the story behind CloudFeaster.

This repo leverages [DockerHub's](https://hub.docker.com/)
[automated build](https://docs.docker.com/docker-hub/builds/) feature to
keep the [simonsdave / cloudfeaster](https://registry.hub.docker.com/u/simonsdave/cloudfeaster/)
docker image up to date.

##Using
[These](docs/using.md) instructions describe
how to author spiders using CloudFeaster and
setup a cloud based infrastructure to host the spiders.

##Contributing
See [these](docs/contributing.md) instructions
describing how to setup your development environment and
start contributing to CloudFeaster.
