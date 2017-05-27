# Change Log
All notable changes to this project will be documented in this file.
Format of this file follows [these](http://keepachangelog.com/) guidelines.
This project adheres to [Semantic Versioning](http://semver.org/).

## [0.9.6] - [2017-xx-xx]

### Added

- added --samples command line option to spiders.py

### Changed

- selenium 3.3.3 -> 3.4.2
- requests 2.13.0 -> 2.16.0

### Removed

- Nothing

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
