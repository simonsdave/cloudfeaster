# TODO

Fine grained list of to do's for the Cloudfeaster project.

## Functional

### Required

* the spidering infrastructure adds various properties to crawl results as illustrated below - to avoid confusing
crawl results with these properties prepend each top level property name with an underscore
```
 "spider": {
   "version": "ae6287c4047e9371e66ff8426b7818418b2d3de5",
   "name": "gaming_spiders.miniclip.MiniclipSpider"
 },
 "crawl_time_in_ms": 6411,
 "status": "Ok",
 "status_code": 0
```
* the spidering infrastructure adds the spider name and version to crawl results - the version
is the hash of the spider's source code - prepend the hash with hashing algorithm's name 
```
 "spider": {
   "version": "ae6287c4047e9371e66ff8426b7818418b2d3de5",
   "name": "gaming_spiders.miniclip.MiniclipSpider"
 },
```
* support proxying of spider traffic through anonymity networks ([Luminati](https://luminati.io/), [Distributed Scraping With Multiple Tor Circuits](http://blog.databigbang.com/tag/crawling-2/), etc)
* use ```selenium.webdriver.Chrome.save_screenshot()``` to capture
  browser window image on spider failure
* spider metadata should include json schema for response

### Nice To Have

* SpiderCrawler currently requires a full spider class name; can this be
  more flexible; some kind of fuzzy matching where the full class name can
  be derived from something less than the full class name

## Operations

* ...

## Performance

* ...

## Documenation

### Required

* describe how docker image tags work and how Cloudfeaster expects them
  to be used - [this](https://medium.com/@mccode/the-misunderstood-docker-tag-latest-af3babfd6375#.x4xg3qhgn)
  is a useful reference

## Stability

* ...

## CI / CD

* ...
