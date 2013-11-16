"""This module is the spider host's mainline with ```run()```
being the entry point."""

import logging
import json

import jsonschema

import clf.jsonschemas


_logger = logging.getLogger("CLF_%s" % __name__)


"""```run()``` executes until failure or ```done``` is ```True```. ```done```
really exists to allow test frameworks to force the main loop to end."""
done = False

"""If ```run()``` ends successfully it returns ```rv_ok```"""
rv_ok = 0


def run(request_queue, response_queue, rr_sleeper):

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
