"""This module is the spider host's mainline with ```run()```
being the entry point."""

import logging
import json

from queues import CrawlResponseQueue


_logger = logging.getLogger("CLF_%s" % __name__)


"""```run()``` executes until failure or ```done``` is ```True```. ```done```
really exists to allow test frameworks to force the main loop to end."""
done = False


def run(crawl_request_queue, crawl_response_queue, rr_sleeper):

    while not done:

        crawl_request = crawl_request_queue.read_message()
        if crawl_request:
            _logger.info("Processing '%s'", crawl_request)
            crawl_response = crawl_request.process()
            # crawl_response is an instance of CrawlResponse ie a dict 
            # write crawl_response to the response queue
            # crawl_response = CrawlResponse(crawl_request, crawl_response)
            # crawl_response_queue.write_message(crawl_response)
            crawl_request.delete()
        else:
            _logger.info("No crawl request to process - sleepin' a bit")
            rr_sleeper.sleep()
