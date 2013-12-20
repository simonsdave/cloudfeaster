"""This module is the spider host's mainline with ```run()```
being the entry point."""

import datetime
import logging
import json

from queues import CrawlResponse

_logger = logging.getLogger("CLF_%s" % __name__)

"""```run()``` executes until failure or ```done``` is ```True```. ```done```
really exists to allow test frameworks to force the main loop to end."""
done = False


def run(crawl_request_queue, crawl_response_queue, rr_sleeper, local_spider_repo):

    while not done:

        crawl_request = crawl_request_queue.read_message()
        if crawl_request:
            _logger.info("Processing '%s'", crawl_request)

            start_time = datetime.datetime.utcnow()

            crawl_response = crawl_request.process(local_spider_repo)

            end_time = datetime.datetime.utcnow()
            crawl_time = end_time - start_time
            crawl_time_in_seconds = round(crawl_time.total_seconds(), 2)

            # start time date in RFC 2822 format (same value as Date HTTP header)
            # ex "Thu, 28 Jun 2001 14:17:15 +0000"
            metrics = {
                "crawl_start_time": start_time.strftime("%a, %d %b %Y %H:%M:%S +0000"),
                "crawl_time_in_seconds": crawl_time_in_seconds,
            }

            crawl_response = CrawlResponse(
                uuid=crawl_request.uuid,
                spider_name=crawl_request.spider_name,
                spider_args=crawl_request.spider_args,
                crawl_response=crawl_response,
                metrics=metrics)

            _logger.info("Writing crawl response '%s'", crawl_response)
            crawl_response_queue.write_message(crawl_response)

            _logger.info("Deleting '%s'", crawl_request)
            crawl_request.delete()
        else:
            _logger.info("No crawl request to process - sleepin' a bit")
            rr_sleeper.sleep()
