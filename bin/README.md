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

* ...

### [install-chromedriver.sh](install-chromedriver.sh)

* ...

## [CircleCI](https://circleci.com)

### [check-circleci-config.sh](check-circleci-config.sh)

* ...

### [check-consistent-clf-version.sh](check-consistent-clf-version.sh)

* ...

### [generate-circleci-config.py](generate-circleci-config.py)

* ...

## Running Spiders

### [run-all-spiders.sh](run-all-spiders.sh)

* ...

* [run-spider.sh](run-spider.sh)

* ...
