"""This module is the spider host's mainline with ```run()```
being the entry point."""

import logging
import json


_logger = logging.getLogger("CLF_%s" % __name__)


"""```run()``` executes until failure or ```done``` is ```True```. ```done```
really exists to allow test frameworks to force the main loop to end."""
done = False


def run(request_queue, response_queue, rr_sleeper):

    while not done:

        message = request_queue.read_message()
        if message:
            _logger.info("Processing message '%s'", message)
            try:
                message.process()
            except Exception as ex:
                _logger.error(
                    "Error processing message '%s' - %s",
                    message,
                    str(ex))
            finally:
                _logger.info("Deleting message '%s'", message)
                message.delete()
        else:
            rr_sleeper.sleep()
