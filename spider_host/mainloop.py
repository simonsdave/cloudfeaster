"""This module is the spider host's mainline with ```run()```
being the entry point."""

import logging

import boto.sqs.connection

import rrsleeper


_logger = logging.getLogger("CLF_%s" % __name__)


"""```run()``` executes until failure or ```done``` is ```True```. ```done```
really exists to allow test frameworks to force the main loop to end."""
done = False

"""If ```run()``` ends successfully it returns ```rv_ok```"""
rv_ok = 0

"""If ```run()``` ends because the request queue can't be found
it returns ```rv_request_queue_not_found```"""
rv_request_queue_not_found = 1

"""If ```run()``` ends because the response queue can't be found
it returns ```rv_response_queue_not_found```"""
rv_response_queue_not_found = 2


def run(
    request_queue_name,
    response_queue_name,
    min_num_secs_to_sleep,
    max_num_secs_to_sleep):

    sqs_conn = boto.sqs.connection.SQSConnection()

    request_queue = sqs_conn.get_queue(request_queue_name)
    if not request_queue:
        _logger.error(
            "Could not find request queue '%s'",
            request_queue_name)
        return rv_request_queue_not_found

    response_queue = sqs_conn.get_queue(response_queue_name)
    if not response_queue:
        _logger.error(
            "Could not find response queue '%s'",
            request_queue_name)
        return rv_response_queue_not_found

    rr_sleeper = rrsleeper.RRSleeper(
        min_num_secs_to_sleep,
        max_num_secs_to_sleep)

    while not done:

        messages = request_queue.get_messages(num_messages=1)
        _logger.info(
            "Read %d messages from queue '%s'",
            len(messages),
            request_queue.name)
        if len(messages):
            message = messages[0]
            try:
                pass
            finally:
                request_queue.delete_message(message)
        else:
            rr_sleeper.sleep()

    return rv_ok
