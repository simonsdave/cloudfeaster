## Development Environment Setup

### [install-dev-env-scripts.sh](install-dev-env-scripts.sh)

* ```install-dev-env-scripts.sh``` is used by spider repos in ```cfg4dev```
to install the Cloudfeaster development environment
* below is example of how ```cfg4dev``` would use ```install-dev-env-scripts.sh```

```bash
pushd "$(git rev-parse --show-toplevel)" > /dev/null

export DEV_ENV_DOCKER_IMAGE=simonsdave/gaming-spiders-xeniel-dev-env:build

if [ -d ./env ]; then
    source ./env/bin/activate
else
    virtualenv env
    source ./env/bin/activate

    pip install --upgrade pip

    CLF_VERSION=v$(grep cloudfeaster== ./setup.py | sed -e "s|^[[:space:]]*['\"]cloudfeaster==||g" | sed -e "s|['\"].*$||g")
    curl -s -L "https://raw.githubusercontent.com/simonsdave/cloudfeaster/${CLF_VERSION}/bin/install-dev-env-scripts.sh" | bash -s --
    unset CLF_VERSION

    ./dev_env/build-docker-image.sh "${DEV_ENV_DOCKER_IMAGE}"
fi

export PATH="$PWD/bin":$PATH

popd > /dev/null
```
### [install-chrome.sh](install-chrome.sh)

* expecting ```install-chrome.sh``` to be used only by various Cloudfeaster
scripts ie. it implements a private "API" so use at your own peril
or, and preferred, don't use ```install-chrome.sh```

### [install-chromedriver.sh](install-chromedriver.sh)

* expecting ```install-chromedriver.sh``` to be used only by various Cloudfeaster
scripts ie. it implements a private "API" so use at your own peril
or, and preferred, don't use ```install-chromedriver.sh```

## [CircleCI](https://circleci.com)

### [generate-circleci-config.py](generate-circleci-config.py)

* ```generate-circleci-config.py``` generates a ```.circleci/config.yaml```
for a spider repo

### [check-consistent-clf-version.sh](check-consistent-clf-version.sh)

* in spider repos the Cloudfeaster version is mentioned in two places (i) ```setup.py```
and (ii) ```.circleci/config.yaml```
* ```check-consistent-clf-version.sh``` is intended to be added to ```.circleci/config.yaml```
and have a zero exit code if the two Cloudfeaster versions are the same or
a non-zero exit code if the two Cloudfeaster versions are different

### [check-circleci-config.sh](check-circleci-config.sh)

* ```check-circleci-config.sh``` is intended to be inserted into ```.circleci/config.yaml```
to confirm the repo's ```.circleci/config.yaml``` is the same as
that generated by ```generate-circleci-config.py```

## Running Spiders

### [run-all-spiders.sh](run-all-spiders.sh)

* call ```run-spider.sh``` for all spiders in a repo

### [run-spider.sh](run-spider.sh)

* runs a spider in a spider repo using ```run_spider.sh miniclip```