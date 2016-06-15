# Spider Authors

### Skills

What skills do I need to author spiders?
In general, the ideal spider author is someone that's automated
website testing using [Selenium 2.0](http://www.seleniumhq.org/projects/webdriver/). More specifically:

1. "get" how HTML websites are built and how to test them using automated tools
1. basic object oriented Python 2.7.x
1. solid understanding of [Selenium 2.0](http://www.seleniumhq.org/projects/webdriver/)
1. good understanding of [XPath](http://en.wikipedia.org/wiki/XPath)

### Getting Started

Let's start with an overview of the spider development process.
Throughout this documentation we'll use [these spiders](https://github.com/simonsdave/gaming-spiders)
and [this](../samples/pypi_spider.py) spider as examples.
Embedded in this documentation is a healthy dose of best practice
guidance as well as required practice.
Best efforts will be made to note when something is best practice.

* create a private or public repo on [github](https://github.com)
* setup the repo to produce a Python distribution with a name
end with ```-spiders``` (this naming convention is important because
it's relied upon by the ```spiders.py``` utility during spider discovery
* connect the repo to Travis - each Travis build should:
  * run pep8/flake8 on the spiders
  * create a pip installable Python package containing all spiders
  * create a docker image with all the spiders
  * push the newly created docker image to a dockerhub that's either public
or has the dockerhub user cloudfeater as a collaborator
* if you know [Python](https://www.python.org), [JSON](http://www.json.org)
and [Selenium](http://www.seleniumhq.org) writing spiders is going to feel
very straightforward
  * best practice recommends creating one spider per ```.py``` file
  * each spider is a Python class derived from ```cloudfeaster.spider.Spider```
  * spiders define metadata which describes the website to be scraped and
the arguments required; arguments are referred to as factors because
they are typically identifying and authenticating factors used to login
to a website on behalf of a user; metadata is expressed in a JSON document
  * spiders also supply a single ```crawl()``` method which is a Selenium script

* ```lots more to fill in here```

## Collaboration

The following outlines the recommended best practice for
how a (small) group of spiders authors can collaborate on authoring
a collection of spiders

* the group can use either the [fork & pull](https://help.github.com/articles/types-of-collaborative-development-models/#fork--pull)
or the [shared repo](https://help.github.com/articles/types-of-collaborative-development-models/#shared-repository-model)
model of collaboration although
the [shared repo model](https://help.github.com/articles/types-of-collaborative-development-models/#shared-repository-model)
has been found to be effective
* with the [shared repo model](https://help.github.com/articles/types-of-collaborative-development-models/#shared-repository-model)
each spider author works in their own topic/feature branch of the repo
* commits to the topic/feature branch will cause a Travis build to be kicked off & each spider author is expected
to monitor those builds and, as required, fix errors
* once the spider author is happy with their commits they
create a [pull request](https://help.github.com/articles/using-pull-requests/)
into the master branch from the topic/feature branch
* once the pull request has been merged, the master branch is built
including building docker images

## Continuous Spider Delivery Pipeline

We've previously reviewed the best practice recommendations
about connecting your spider github repo to
Travis, Travis building your spider docker image and
Travis pushing the image to DockerHub. If you've done this
then you've achieved your goal of creating a continuous spider
delivery pipeline. How? Before running a spider, Cloudfeaster
Services confirms it has the latest copy of your docker image
and if required downloads the latest/updated docker image.

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

* Cloudfeaster Services will cache the results of running a spider
for the number of seconds defined by the ```ttl``` property of a
spider's metadata.
* if the ```ttl``` property is missing 60 is assumed
* ```ttl``` must be at least 60 (screen scraping web sites with info
that often takes a bit to refresh and thus the rational for the
minimum ```ttl``` value of 60)

```python
class MySpider(spider.Spider):

    @classmethod
    def get_metadata(self):
        return {
            'url': 'https://example.com',
            'ttl': 120,
```

### Factor Display Names

* [locale](https://en.wikipedia.org/wiki/Locale)
* ```LANG``` environment variable which will look something like ```en_CA.UTF-8``` - take the first 2 characters
and this will be the [ISO639-2](http://www.loc.gov/standards/iso639-2/php/code_list.php) language code

```python
'factor_display_names': {
    'email': {
        'en': 'e-mail',
        'fr': 'e-mail',
        'ja': '電子メール',
    },
    'password': {
        'en': 'Password',
        'fr': 'mot de passe',
        'ja': 'パスワード',
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

### Development and Runtime Environmental Differences

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

### Performance

Performance = how can I make my spiders run faster?

Cloudfeaster's approach of using [Selenium+WebDriver (aka Selenium 2.0)](http://www.seleniumhq.org/projects/webdriver/) makes it super easy to create spiders that are very resilient to web site changes. Ease of implementation and maintenance comes at the expense of performance. How can I improve the performance of my Cloudfeaster spiders?
All [Selenium+WebDriver (aka Selenium 2.0)](http://www.seleniumhq.org/projects/webdriver/) based
spiders inherit their performance characteristics from the cost of spinning up and driving a real browser. To make significant progress on performance you've got to avoid spinning up browsers.

Some practical details on how to avoid using real browsers ... the [Selenium+WebDriver (aka Selenium 2.0)](http://www.seleniumhq.org/projects/webdriver/) spiders all derive from [webdriver_spider.Spider](https://github.com/simonsdave/cloudfeaster/blob/master/clf/webdriver_spider.py#L29).
One approach to making your spiders really fast would be to create a new abstract base class which derives from [spider.Spider](https://github.com/simonsdave/cloudfeaster/blob/master/clf/spider.py#L22) and integrates with one of the [existing libraries](https://github.com/simonsdave/cloudfeaster/wiki/Other-Web-Scraping-Utilities-&-Approaches#utilities) which makes it easier to create a network traffic based spider. This approach will avoid the overhead of spinning up real browsers and yet still allow you to take advantage of Cloudfeaster's other features.

## Resources

* [inDifferent Languages](http://www.indifferentlanguages.com/words/e-mail) - How Do You Say Different English Words and Expressions in Different Languages - examples
  * [e-mail](http://www.indifferentlanguages.com/words/e-mail)
  * [password](http://www.indifferentlanguages.com/words/password)
