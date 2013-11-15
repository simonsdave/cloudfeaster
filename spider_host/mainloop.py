"""This module is the spider host's mainline with ```run()```
being the entry point."""

import logging
import json

import boto.sqs.connection
import jsonschema

import clf.jsonschemas


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
    rr_sleeper):

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

    while not done:

        messages = request_queue.get_messages(1)
        _logger.debug(
            "Read %d messages from queue '%s'",
            len(messages),
            request_queue.name)
        if len(messages):
            message = messages[0]
            message_body = message.get_body()
            _logger.info("Processing message '%s'", message_body)
            try:
                message_body_as_dict = json.loads(message_body)
                jsonschema.validate(
                    message_body_as_dict,
                    clf.jsonschemas.crawl_request)
                _process(message_body_as_dict)
            except Exception as ex:
                _logger.error(
                    "Error processing message '%s' - %s",
                    message_body,
                    str(ex))
            finally:
                request_queue.delete_message(message)
        else:
            rr_sleeper.sleep()

    return rv_ok


def _process(request):
    pass
