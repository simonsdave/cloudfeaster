# Story

## The Opportunity

Whether used for content acquisition or business process automation,
web scraping or spidering is a key enabler of many thriving businesses.
But writing spiders is hard and while
there are [lots of screen scraping utilities](other_screen_screen_scapers.md)
available these utilities tend to solve only a piece of the overall problem.
There is a distinct lack of an operationally complete and enterprise ready
solution which:

1. makes it easy to author spiders that a robust enough to survive
many types of web site change
1. provides an infrastructure that makes it easy to run spiders
through a well defined (RESTful) API
1. detects spider failure and gathers enough evidence on failure
that debugging spider failure is easy

Why is it so hard to write a spider?
When someone uses a web browser to surf the web, the web browser
generates network traffic to interact with a web server.
Traditional spiders are written to mimic this network traffic.
However, it’s hard to write these kinds of spiders and it’s getting much
harder as web sites increasingly leverage AJAX patterns.
In addition, this approach to spider writing creates spiders that are very brittle -
even minor web site changes can cause spiders to break
in ways that are hard to debug.

## Trends

There are some very important trends which can be leveraged to realize
our spidering dreams.

### Automated Testing Trends

The wide spread adoption of automated testing has fueled some important trends/milestones:

1. web sites are being built to be tested using automated mechanisms
1. automated testing tools have become very robust
  - [Chrome supporting headless mode](https://developers.google.com/web/updates/2017/04/headless-chrome)
  - [Chrome's DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
  - [ChromeDriver using the DevTools Protocol to implement WebDriver protocol](https://sites.google.com/a/chromium.org/chromedriver/)
  - [standardization of WebDriver protocol](https://w3c.github.io/webdriver/webdriver-spec.html)
  - [Python binding of the WebDriver protocol](https://seleniumhq.github.io/selenium/docs/api/py/index.html))
1. lots of "QA automation" companies are very familiar with Selenium WebDriver

### IaaS Trends

1. the number of IaaS providers continues to increase
1. IaaS costs continue to drop
1. an increasing number of very capable CI services
are being built on IaaS offerings
1. efficiently running and isolating a variety of workload types
on an IaaS offering at scale has become easier with [Docker](https://www.docker.com/)
and [Kubernetes](https://kubernetes.io/)

## The Cloudfeaster Approach

Write spiders using a high level scripting language (Python)
using tools/APIs designed for automated testing ([Selenium](http://www.seleniumhq.org/)).
Package collections of spiders in a [Docker](https://www.docker.com/) image.
This means:

  * spiders are easy to write
  * spiders are reliable even in the face of most web site changes
  * it's possible to outsource spider development and maintenance

Use a RESTful API for discovering and running spiders.
The service implementing the RESTful API is hosted on an IaaS provider.
To run a spider, the service locates the [Docker](https://www.docker.com/) image
containing the spider, makes sure the latest version of the [Docker](https://www.docker.com/) image
is available and uses the latest [Docker](https://www.docker.com/) image to
create a [Docker](https://www.docker.com/) container in which the spider is run.
Inside the [Docker](https://www.docker.com/) container a headless browser
is started and the spider runs against that headless browser.
Use [Kubernetes](https://kubernetes.io/) for all orchestration and operation
of [Docker](https://www.docker.com/) containers to both run the service
behind the RESTful API and run the spiders .
