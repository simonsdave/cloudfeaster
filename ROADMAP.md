#Roadmap

##v0.9
* RESTful API to discover available spiders and run spiders
* spiders run in docker containers
* no concurrency control
* framework for authoring spiders and docker image to run spiders

##v1.0
* concurrency control

##Future
* [Luminati Anonymity Network](http://luminati.io)
* when a spider fails create screenshot of the browser in
the failed state using ```webdriver.Chrome.get_screenshot_as_file()```
* caching of crawl results in API tier
* webhook called when crawl completes
* notification when crawl completes using WebSocket
