# TODO

Fine grained list of to do's for the Cloudfeaster project.

## Functional

### Required

* spider metadata should include json schema for response
* use ```selenium.webdriver.Chrome.save_screenshot()``` to capture
  browser window image on spider failure
* support proxying of spider traffic through anonymity networks ([Luminati](https://luminati.io/), [Distributed Scraping With Multiple Tor Circuits](http://blog.databigbang.com/tag/crawling-2/), etc)

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
