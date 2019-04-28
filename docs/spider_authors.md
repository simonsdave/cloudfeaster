# Spider Authors

## Skills

What skills do I need to author spiders?
In general, the ideal spider author is someone that's automated
website testing using [Selenium 2.0](http://www.seleniumhq.org/projects/webdriver/). More specifically, a spider author should:

1. get how websites are built and how to test them using automated tools
1. understand the fundamentals of object oriented Python 2.7.x,
[JSON](http://www.json.org),
[Selenium WebDriver](http://www.seleniumhq.org/projects/webdriver/) and
probably [XPath](http://en.wikipedia.org/wiki/XPath)

## Getting Started

Let's begin with an overview of the spider development process.
In this documentation we'll use [these spiders](https://github.com/simonsdave/gaming-spiders) as examples.
Embedded in this documentation is a healthy dose of best practice
guidance as well as required practice.
Best efforts will be made to note when something is best practice.

* create a private or public repo on [github](https://github.com)
* setup the repo to produce a Python distribution with a distribution name
ending in ```-spiders``` (this naming convention is important because
it's relied upon by Cloudfeaster during spider discovery
* connect the repo to a CI service and configure CI to run a build on at least a nightly basis (so you have daily feedback on if your spiders are broken)
* best practice recommends creating one spider per ```.py``` file
* each spider is a Python class derived from ```cloudfeaster.spider.Spider```
* spiders define metadata which describes the website to be scraped and
the crawl arguments required
* crawl arguments are referred to as factors because
they are typically identifying and authenticating factors used to login
to a website on behalf of a user
* metadata is expressed in a JSON document and is validated against
[this](../cloudfeaster/jsonschemas/spider_metadata.json) [jsonschema](http://json-schema.org/)
* spiders are required to supply a single ```crawl()``` method which has
2 + number of factors arguments
* the body of the ```crawl()``` method is where the spider author
writes [Selenium WebDriver](http://www.seleniumhq.org/projects/webdriver/)
script
* Cloudfeaster spiders adapt well to changing websites and variable networks - [this](https://selenium-python.readthedocs.io/waits.html)
describes Selenium explicit and implicit waits - Cloudfeaster supports both implicit and explicit waits however using explicit waits is recommended because it results in spiders with better
resiliency characteristics

## Branching and Versioning Strategy

* the master branch ... :TODO: [protected branch](https://help.github.com/en/articles/about-protected-branches)
* all development is done on topic branches created from the master branch
* :TODO: [pull request](https://help.github.com/articles/using-pull-requests/)
* use [Semantic Versioning](http://semver.org/)
* for each release a new branch is created from master called ```release-<version>```

## Collaboration

The following outlines the recommended best practice for
how a (small) group of spiders authors can collaborate on authoring
a collection of spiders

* teams of spider authors use
the [collaborative development model](https://help.github.com/en/articles/about-collaborative-development-models)
collaboration model
* spider authors work in topic branches
* once the spider author is happy with the changes they
create a [pull request](https://help.github.com/articles/using-pull-requests/)
into the master branch from the topic branch
* use [semantic commit messages](https://seesparkbox.com/foundry/semantic_commit_messages)
* per [this article](https://thoughtbot.com/blog/better-commit-messages-with-a-gitmessage-template) ```~/.gitconfig``` should look something like below - in particular note ```template```

```
[user]
name = Dave Simons
email = simonsdave@gmail.com
[commit]
template = ~/.gitmessage
```

* ```~/.gitmessage``` is referenced by ```template``` above

```
feat: add hat wobble
^--^  ^------------^
|     |
|     +-> Summary in present tense.
|
+-------> Type: chore, docs, feat, fix, refactor, style, or test.

chore: add Oyster build script
docs: explain hat wobble
feat: add beta sequence
fix: remove broken confirmation message
refactor: share logic between 4d3d3d3 and flarhgunnstow
style: convert tabs to spaces
test: ensure Tayne retains clothing
```

## Continuous Spider Delivery Pipeline

* :TODO: need to complete this section based

## Overview of a Spider's Structure

First a spider with no factors.

```python
```

Now a spider with factors.

```python
```

## Metadata

* ...

### TTL

* Cloudfeaster caches crawl results
for the time specified by the ```ttl``` property of a
spider's metadata.
* ```60s``` is the default value for ```ttl``` meaning that cloudfeaster
caches crawl results for 60 seconds
* ```ttl``` is a string property of the form ```<number><duration>```
where ```<number>``` is an non-zero integer and ```<duration>``` is one
of ```s```, ```m```, ```h``` or ```d``` representing seconds, minutes, hours
and days respectively

```python
class MySpider(spider.Spider):

    @classmethod
    def get_metadata(self):
        return {
            'url': 'https://example.com',
            'ttl': '1h',
        }
```

### Paranoia Level

* some web site owners do not like spiders crawling their web sites
and put in place mechanisms to defend against crawling
* Cloudfeaster uses various approaches for circumventing these defenses
* over time these defenses will evolve
* spider authors can optionally add a ```paranoiaLevel``` property
to a spider's metadata to describe how serious a web site owner is
about defending against crawling
* ```low``` is the default value for ```paranoiaLevel``` with ```medium```
and ```high``` being the other permissible values
* based on the ```paranoiaLevel```, Cloudfeater will select appropriate
circumventing approach with ```low``` meaning Cloudfeaster does nothing
* one word of caution - spider authors should expect that setting ```paranoiaLevel```
to ```high``` will cause a spider to run slower and cost more to run that setting ```paranoiaLevel```
to  ```low```

```python
class MySpider(spider.Spider):

    @classmethod
    def get_metadata(self):
        return {
            'url': 'https://example.com',
            'paranoiaLevel': 'low',
        }
```

### Maximum Crawl Concurrency

* spider authors can optionally define the spider metadata property ```maxConcurrentCrawls```
which defines the maximum number of spiders which can be concurrently crawling
a web site - this concurrency level is enforced by the Cloudfeaster infrastructure
* 3 is the default value for ```maxConcurrentCrawls``` and 1 and 25 are the
minimum and maximum values respectively
* motivation for setting an upper bound on the number of concurrent crawls is
exactly the same as ```paranoiaLevel``` = some website owners are very sensitive
to spiders crawling their websites

```python
class MySpider(spider.Spider):

    @classmethod
    def get_metadata(self):
        return {
            'url': 'https://example.com',
            'maxConcurrentCrawls': 5,
        }
```

### Maximum Crawl Time

* by defining ```maxCrawlTime``` spider authors can
declare the maximum time needed for a spider crawl to a website
* ```30s``` is the default value for ```maxCrawlTime```
* ```maxCrawlTime``` is a string property of the form ```<number><duration>```
where ```<number>``` is a non-zero integer and ```<duration>``` is one
of ```s``` or ```m``` representing seconds and minutes respectively


```python
class MySpider(spider.Spider):

    @classmethod
    def get_metadata(self):
        return {
            'url': 'https://example.com',
            'maxCrawlTime': '45s',
        }
```

### Identifying and Authenticating Factors

* when your spider needs to login to a website on behalf of a user, the username
and password for the user needs to be available to the spider at crawl time
but should not be hard coded into the spider
* naming convention
    * identifying factors (ex username) are used to identify a user
    * authenticating factors (ex password) are used to verify (authenticate) a user's identity
* why differentiate between identifying and authenticating factors? if you're building
a UI that dynamically adapts to available spiders you're going to want to know when
a factor is, for example, a password because you don't want to echo back the plaintext
password as the user types it in
* the [pypi.py](../cloudfeaster/samples/pypi.py) provides a complete example
of how to describe, gather and use identifying and authenticating factors - key things to
note in this example:
    * ```# -*- coding: utf-8 -*-``` at the top of the file so the spider's source file is appropriately [encoded](https://www.python.org/dev/peps/pep-0263/) and this is particularly important with factor display names (see below)
    * ```get_metadata()``` includes 4 metadata properties
        * ```identifyingFactors``` describes the spider's identifying factors
        * ```authenticatingFactors``` describes the spider's authenticating factors
        * ```factorDisplayOrder``` describes the order in which UIs should display/prompt for factors
        * ```factorDisplayNames``` see below
    * ```crawl()``` and ```_crawl()``` have arguments that match the metadata
    * ```_crawl()``` uses the factors
    * ```spider.CLICrawlArgs``` demonstrates how to dynamically build a CLI to gather factors based on spider's metadata

### Factor Display Names

* [locale](https://en.wikipedia.org/wiki/Locale)
* ```LANG``` environment variable which will look something like ```en_CA.UTF-8``` - take the first 2 characters
and this will be the [ISO639-2](http://www.loc.gov/standards/iso639-2/php/code_list.php) language code

```python
'factorDisplayNames': {
    'email': {
        'en': 'e-mail',
        'fr': 'e-mail',
        'ja': u'電子メール',
    },
    'password': {
        'en': 'Password',
        'fr': 'mot de passe',
        'ja': u'パスワード',
    },
},
```

* per above, with factor display names & encoding ...

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
```

* to try different factor display names try something like ...

```bash
>LANG=ja ./spider.py
```

## Development and Runtime Environmental Differences

Cloudfeaster spiders can be developed on pretty much
any operating systems/browser combo that's capable of
running Selenium
but Cloudfeaster Services always runs spiders on Ubuntu and Chrome;
some web sites present different responses to browser
requests based on the originating browser and/or operating system
as derived from the originating browser's user agent header;
if, for example, development of a spider is done on Mac OS X
using Chrome, the xpath expressions embedded in the spider may
not be valid when the spider is run on Ubuntu using Chrome;
to address this disconnect, spider authors can force Cloudfeaster
Services to use a user agent header that matches their development
environment by providing a value for the ```user_agent``` argument
of ```Browser``` class' constructor.

### User Agent Headers

How do I find out the user agent header?
Try [this](http://www.whoishostingthis.com/tools/user-agent/) web site.

### Google Chrome Version

How do I figure out what version of Chrome I'm using?
On Ubuntu try ```google-chrome --version```.

### Performance

Performance = how can I make my spiders run faster?

Cloudfeaster's approach of using [Selenium+WebDriver (aka Selenium 2.0)](http://www.seleniumhq.org/projects/webdriver/) makes it super easy to create spiders that are very resilient to web site changes. Ease of implementation and maintenance comes at the expense of performance. How can I improve the performance of my Cloudfeaster spiders?
All [Selenium+WebDriver (aka Selenium 2.0)](http://www.seleniumhq.org/projects/webdriver/) based
spiders inherit their performance characteristics from the cost of spinning up and driving a real browser. To make significant progress on performance you've got to avoid spinning up browsers.

Some practical details on how to avoid using real browsers ... the [Selenium+WebDriver (aka Selenium 2.0)](http://www.seleniumhq.org/projects/webdriver/) spiders all derive from [webdriver_spider.Spider](https://github.com/simonsdave/cloudfeaster/blob/master/clf/webdriver_spider.py#L29).
One approach to making your spiders really fast would be to create a new abstract base class which derives from [spider.Spider](https://github.com/simonsdave/cloudfeaster/blob/master/clf/spider.py#L22) and integrates with one of the [existing libraries](https://github.com/simonsdave/cloudfeaster/wiki/Other-Web-Scraping-Utilities-&-Approaches#utilities) which makes it easier to create a network traffic based spider. This approach will avoid the overhead of spinning up real browsers and yet still allow you to take advantage of Cloudfeaster's other features.

## Environment Variables

### CLF_REMOTE_CHROMEDRIVER

By default, spiders run inside a docker container which
means it can be hard to debug spiders during development.
Try staring [ChromeDriver](http://chromedriver.chromium.org/)
on the host machine.

![](images/starting-chromedriver.png)

We now want the spider running in the container
to use the ChromeDriver we just started which means the ChromeDriver
will use the host's Chrome and you'll be able to watch the
spider execute. Below illustrates how to do this by setting
the ```CLF_REMOTE_CHROMEDRIVER``` environment variable.

```bash
(env)>export CLF_REMOTE_CHROMEDRIVER=http://host.docker.internal:9515
(env)>run-spider.sh msnonlinegames | jq .
{
  "1": {
    "link": "http://zone.msn.com/en/mssolitairecollection/default.htm?intgid=hp_populargames_1",
    "title": "Microsoft Solitaire Collection"
  },
  "2": {
    "link": "http://zone.msn.com/en/mahjonggdimensions/default.htm?intgid=hp_populargames_2",
    "title": "Mahjongg Dimensions"
  },
  "3": {
    "link": "http://zone.msn.com/en/mahjonggtoychesthtml5/default.htm?intgid=hp_populargames_3",
    "title": "Mahjongg Toy Chest"
  },
  "4": {
    "link": "http://zone.msn.com/en/bubbleshooter/default.htm?intgid=hp_populargames_4",
    "title": "Bubble Shooter"
  },
  "5": {
    "link": "http://zone.msn.com/en/bejeweled3/default.htm?intgid=hp_populargames_5",
    "title": "Bejeweled 3"
  },
  "_debug": {},
  "_metadata": {
    "status": {
      "message": "Ok",
      "code": 0
    },
    "spiderArgs": [],
    "spider": {
      "version": "sha1:7b766165eb1c690b994ff055998c088e496179da",
      "name": "__main__.MSNOnlineGamesSpider"
    },
    "crawlTime": {
      "started": "2019-03-31T16:50:44.803774+00:00",
      "durationInMs": 6691
    }
  }
}
~>
```

[This](https://docs.docker.com/docker-for-mac/networking/) explains
how we arrived at the ```host.docker.internal``` host name and
the ```9515``` is the default port on which ChromeDriver listens.

### CLF_CHROME

### CLF_CHROME_OPTIONS

## Resources

* [inDifferent Languages](http://www.indifferentlanguages.com/words/e-mail) - How Do You Say Different English Words and Expressions in Different Languages - examples
  * [e-mail](http://www.indifferentlanguages.com/words/e-mail)
  * [password](http://www.indifferentlanguages.com/words/password)
* WebDriver Waits
  * [25 Jan '17 - Best Practice: Use Explicit Waits](https://wiki.saucelabs.com/display/DOCS/Best+Practice%3A+Use+Explicit+Waits)
