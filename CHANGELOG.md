# Change Log
All notable changes to this project will be documented in this file.
Format of this file follows [these](http://keepachangelog.com/) guidelines.
This project adheres to [Semantic Versioning](http://semver.org/).

## [%RELEASE_VERSION%] - [%RELEASE_DATE%]

### Added

* Nothing

### Changed

* ```bin/install_chrome.sh``` -> ```bin/install-chrome.sh```
* ```bin/install_chromedriver.sh``` -> ```bin/install-chromedriver.sh```

### Removed

* remove ```bin/chromedriver_version.sh``` since this script was no longer used
* remove ```dev-env-version``` label from docker image since this label is no longer used

## [0.9.20] - [2019-05-19]

### Added

* add ```check-consistent-clf-version.sh``` to ```setup.py``` as script which is installed
as part of the Cloudfeaster python package

### Changed

* Nothing

### Removed

* Nothing

## [0.9.19] - [2019-05-19]

### Added

* add ```install-dev-env-scripts.sh``` for use in CircleCI pipeline

### Changed

* Nothing

### Removed

* Nothing

## [0.9.18] - [2019-05-18]

### Added

* add ```check-consistent-dev-env-version.sh``` to CircleCI pipeline
* add ```run-bandit.sh``` to CircleCI pipeline
* add ```.cut-release-version.sh``` in support of using new revs of [dev-env](https://github.com/simonsdave/dev-env)

### Changed

* renamed ```run_sample.sh``` -> ```run-sample.sh```
* the ```ttlInSeconds``` property in spider metadata is now ```ttl``` and the value associated
with the property is now a string instead of an integer - the string
has the form ```<number><duration>```
where ```<number>``` is a non-zero integer and ```<duration>``` is one
of ```s```, ```m```, ```h``` or ```d``` representing seconds, minutes, hours
and days respectively
* the ```maxCrawlTimeInSeconds``` spider metadata property is now ```maxCrawlTime```
and is also a string instead of an integer - the string
has the form ```<number><duration>```
where ```<number>``` is a non-zero integer and ```<duration>``` is one
of ```s``` or ```m``` representing seconds and minutes respectively
* ```dev-env``` 0.5.15 -> 0.5.19
* sha1 -> sha256 after running [bandit](https://github.com/PyCQA/bandit)

### Removed

* Nothing

## [0.9.17] - [2019-04-15]

### Added

* ```bin/install-dev-env-scripts.sh``` can now be used by spider repos to add dev env host scripts to a spider repo's host env

### Changed

* Nothing

### Removed

* Nothing

## [0.9.16] - [2019-04-01]

### Added

* added ```run-all-spiders.sh``` and ```run-spider.sh```
* by default Chrome now started with ```--no-sandbox``` which should mean that
Chrome can run as root which simplifies a whole host of complexity

### Changed

* Nothing

### Removed

* Nothing

## [0.9.15] - [2019-03-30]

### Added

- .travis.yml now runs ```run_repo_security_scanner.sh```
- added ```xe_exchange_rates.py``` sample spider
- added sha1 hash of spiders args to spider output

### Changed

- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver) 2.38 -> 2.46
- Selenium 3.12.0 -> 3.141.0
- twine 1.11.0 -> 1.12.1
- dateutil 2.7.3 -> 2.7.5
- material simplifcation of way to use ```run_sample.sh```

### Removed

- removed ```bank_of_canada_daily_exchange_rates.py``` sample spider
- removed ```spiderhost.py```, ```spiderhost.sh```, ```spiders.py``` and ```spiders.sh```

## [0.9.14] - [2018-05-30]

### Added

- Nothing

### Changed

- Selenium 3.11.0 -> 3.12.0
- python-dateutil 2.7.2 -> 2.7.3
- spider metadata changed to camel case instead of snake case to get closer to [these](https://google.github.io/styleguide/jsoncstyleguide.xml) JSON style guidelines
- crawl results metadata now grouped in the ```_metadata``` property and use camel case instead of snake case
- crawl results are now validated against [this](cloudfeaster/jsonschemas/spider_output.json) jsonschema
- added [spiders.sh](bin/spiders.sh) and [spiderhost.sh](bin/spiderhost.sh) to enable the API for a docker image container spiders to be expressed in a manner that's independant from Python and Webdriver

### Removed

- Nothing

## [0.9.13] - [2018-04-24]

### Added

- support [pip 10.x](https://pip.pypa.io/en/stable/news/)

### Changed

- simonsdave/cloudfeaster docker image is now based on Ubuntu 16.04
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver) 2.37 -> 2.38

### Removed

- Nothing

## [0.9.12] - [2018-04-07]

### Added

- added [cloudfeaster/samples/pypi.py](cloudfeaster/samples/pypi.py) sample spider

### Changed

- spiders meta data - url string property is now validated using jsonschema
uri format instead of pattern
- selenium 3.9.0 -> 3.11.0
- python-dateutil 2.6.1 -> 2.7.2
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver) 2.35 -> 2.37
- twine 1.10.0 -> 1.11.0
- identifying_factors and authenticating_factors properties will now always appear
in ```spiders.py``` output

### Removed

- Nothing

## [0.9.11] - [2018-02-26]

### Added

- Nothing

### Changed

- samples/pypi_spider.py -> samples/pythonwheels_spider.py
- spider metadata property name change = max_concurrency -> max_concurrent_crawls

### Removed

- Nothing

## [0.9.10] - [2018-02-09]

### Added

- Nothing

### Changed

- Selenium 3.8.1 -> 3.9.0

### Removed

- Nothing

## [0.9.9] - [2018-02-02]

### Added

- Nothing

### Changed

- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver) 2.34 -> 2.35

### Removed

- Nothing

## [0.9.8] - [2018-01-10]

### Added

- ```max concurrency``` per spider property is now part of
the output from ```Spider.get_validated_metadata()``` regardless
of whether or not it is specified as part of the explicit spider
metadata declaration
- added ```paranoia_level``` to spider metadata
- added ```max_crawl_time_in_seconds``` to spider metadata
- ```ttl_in_seconds``` now has an upper bound of 86,400 (1 day in seconds)
- ```max_concurrency``` now has an upper bound of 25

### Changed

- Selenium 3.7.0 -> 3.8.1
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver) 2.33 -> 2.34
- *breaking change* ```ttl``` -> ```ttl_in_seconds``` in spider metadata

### Removed

- Nothing

## [0.9.7] - [2017-11-27]

### Added

- added ```.prep-for-release-master-branch-changes.sh``` so package version number
is automatically bumped when cutting a relase
- ```.prep-for-release-master-branch-changes.sh``` now generates Python packages
for [PyPI](https://pypi.python.org/pypi) from release branch

### Changed

- bug fix in ```.prep-for-release-release-branch-changes.sh``` to links in main ```README.md```
work correctly after a release

### Removed

- removed ```cloudfeaster.util``` module since it wasn't used

## [0.9.6] - [2017-11-25]

### Added

- added --log command line option to spiders.py
- added --samples command line option to spiders.py
- ```cloudfeaster.webdriver_spider.WebElement``` now has
a ```is_element_present()``` method that functions just
like ```cloudfeaster.webdriver_spider.Browser```

### Changed

- per [this article](https://developers.google.com/web/updates/2017/04/headless-chrome)
  [headless Chrome](https://chromium.googlesource.com/chromium/src/+/lkgr/headless/README.md)
  is now available and ```Cloudfeaster``` will use it by default which means we're also
  able to remove the need to [Xvfb](https://en.wikipedia.org/wiki/Xvfb) which is a really
  nice simplification and reduction in required crawling resources - also, because we're
  removing [Xvfb](https://en.wikipedia.org/wiki/Xvfb) ```bin/spiderhost.sh``` was also removed
- selenium 3.3.3 -> 3.7.0
- requests 2.13.0 -> >=2.18.2
- ndg-httpsclient 0.4.2 -> 0.4.3
- [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver) 2.29 -> 2.33
- [simonsdave/cloudfeaster](https://hub.docker.com/r/simonsdave/cloudfeaster/) docker image
now uses the latest version of pip

### Removed

- removed all code related to Signal FX

## [0.9.5] - [2017-04-17]

### Added

- pypi_spider.py now included with distro in cloudfeaster.samples

### Changed

- upgrade selenium 3.0.2 -> 3.3.3
- upgrade chromedriver 2.27 -> 2.29

### Removed

- Nothing

## [0.9.4] - [2017-03-05]

### Added

- added _crawl_time to crawl results

### Changed

- upgrade to [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver) 2.27
from 2.24

### Removed

- Nothing

## [0.9.3] - [2017-03-03]

### Added

- Nothing

### Changed

- fix crawl response key errors - _status & _status_code in crawl
response were missing the leading underscore for the following responses

    - SC_CTR_RAISED_EXCEPTION
    - SC_INVALID_CRAWL_RETURN_TYPE
    - SC_CRAWL_RAISED_EXCEPTION
    - SC_SPIDER_NOT_FOUND

### Removed

- Nothing

## [0.9.2] - [2017-02-12]

### Added

- Nothing

### Changed

- dev env upgraded to docker 1.12
- *BREAKING CHANGE* = selenium 2.53.6 -> 3.0.1 which resulted in
  requiring an upgrade to
  [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver) 2.24
  from 2.22 and it turns out 2.22 does not work with selenium 3.0.1
- spider version # in crawl results now include hash algo along
  with the hash value
- *BREAKING CHANGE* = the spidering infrastructure augments crawl results
  with data such as the time to crawl, spider name & version number, etc - in
  order to more easily differentiate crawl results from augmented data, the
  top level property names for all augment data is now prefixed with an underscore - as
  an example, below shows the new output from running the [PyPI](https://pypi.python.org/pypi)
  sample spider
```bash
>./pypi_spider.py | jq .
{
  "virtualenv": {
    "count": 46718553,
    "link": "http://pypi-ranking.info/module/virtualenv",
    "rank": 5
  },
  "_status_code": 0,
  "setuptools": {
    "count": 63758431,
    "link": "http://pypi-ranking.info/module/setuptools",
    "rank": 2
  },
  "simplejson": {
    "count": 182739575,
    "link": "http://pypi-ranking.info/module/simplejson",
    "rank": 1
  },
  "requests": {
    "count": 53961784,
    "link": "http://pypi-ranking.info/module/requests",
    "rank": 4
  },
  "six": {
    "count": 54950976,
    "link": "http://pypi-ranking.info/module/six",
    "rank": 3
  },
  "_spider": {
    "version": "sha1:ccb6a042dd11f2f7fb7b9541d4ec888fc908a8ef",
    "name": "__main__.PyPISpider"
  },
  "_crawl_time_in_ms": 4773,
  "_status": "Ok"
}
```
- upgrade dev env to docker 1.12

### Removed

- Nothing

## [0.9.1] - [2016-08-17]

### Added

- Nothing

### Changed

- fixed bug that was duplicating crawl response data in ```CrawlResponseOk```

### Removed

- Nothing

## [0.9.0] - [2016-08-16]

### Added

- support docker 1.12

### Changed

- version bumps for dependancies:
    - chromedriver 2.22
    - selenium 2.53.6
    - requests 2.11.0
    - ndg-httpsclient 0.4.2
- set of simplifications in dev env setup

### Removed

- temporary removal of authenticated proxy support

## [0.8.0] - [2016-06-14]

### Added

- Cloudfeaster spiders can be developed on pretty much
any operating systems/browser combinations that can
run Selenium
but Cloudfeaster Services always runs spiders on Ubuntu and Chrome;
some web sites present different responses to browser
requests based on the originating browser and/or operating system;
if, for example, development of a spider is done on Mac OS X
using Chrome, the xpath expressions embedded in a spider may
not be valid when the spider is run on Ubuntu using Chrome;
to address this disconnect, spider authors can force Cloudfeaster
Services to use a user agent header that matches their development
environment by providing a value for the ```user_agent``` argument
of ```Browser``` class' constructor.

## [0.7.0] - [2016-05-03]

### Added

- added proxy support to permit use of anonymity networks like those listed below - proxy support is exposed
by 2 new flags in ```spiderhost.py``` (```--proxy``` and ```--proxy-user```)
    - [Luminati](https://luminati.io/)
    - [Crawlera](http://crawlera.com/)
    - [WonderProxy](https://wonderproxy.com/)
    - [Distributed Scraping With Multiple Tor Circuits](http://blog.databigbang.com/tag/crawling-2/)

```
>spiderhost.py --help
Usage: spiderhost.py <spider> [<arg1> ... <argN>]

spider hosts accept the name of a spider, the arguments to run the spider and
optionally proxy server details. armed with all this info the spider host runs
a spider and dumps the result to stdout.

Options:
  -h, --help            show this help message and exit
  --log=LOGGING_LEVEL   logging level
                        [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - default =
                        ERROR
  --proxy=PROXY         proxy - default = None
  --proxy-user=PROXY_USER
                        proxy-user - default = None
>
>spiderhost.py --proxy=abc
Usage: spiderhost.py <spider> [<arg1> ... <argN>]

spiderhost.py: error: option --proxy: required format is host:port
>
>spiderhost.py --proxy-user=abc
Usage: spiderhost.py <spider> [<arg1> ... <argN>]

spiderhost.py: error: option --proxy-user: required format is user:password
>
```

## [0.6.0] - [2016-01-24]

### Changed

- colorama now req'd to be @ least version 0.3.5 instead of only 0.3.5

- command line args to bin/spiderhost.sh have been simplified - now just
  take spider name and spider args just as you'd expect - no more url
  encoding of args and ----- indicating no spider args

- like the changes to bin/spiderhost.sh, bin/spiderhost.py now just accepts
  regular command line arguments of a spider name and spider args - much easier

### Removed

- bin/spiders.sh is no longer needed - callers now access bin/spiders.py
  directly rather that getting at bin/spiders.py through bin/spiders.sh

## [0.5.0] - [2015-05-10]

- not really the initial release but intro'ed CHANGELOG.md late
- initial clf commit to github was 13 Oct '13
