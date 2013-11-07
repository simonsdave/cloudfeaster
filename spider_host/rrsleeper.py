"""..."""

import logging
import random
import time

_logger = logging.getLogger("CLF_%s" % __name__)

class RRSleeper(object):

    def __init__(self, min_num_secs_to_sleep, max_num_secs_to_sleep):
        object.__init__( self )
        self._min_num_secs_to_sleep = min_num_secs_to_sleep
        self._max_num_secs_to_sleep = max_num_secs_to_sleep
    
    def sleep(self):
        """Returns the number of seconds slept."""
        num_secs_to_sleep_as_float = random.uniform(
            self._min_num_secs_to_sleep,
            self._max_num_secs_to_sleep)
        num_secs_to_sleep = int(round(num_secs_to_sleep_as_float))
        _logger.info(
            "Sleeping for %d (%d,%d) seconds",
            num_secs_to_sleep,
            self._min_num_secs_to_sleep,
            self._max_num_secs_to_sleep)
        time.sleep(num_secs_to_sleep)
        return num_secs_to_sleep
