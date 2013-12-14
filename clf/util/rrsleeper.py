"""Given the polling style of interacting with AWS SQS an
often used access pattern is a never ending while looping
asking an SQS queue if there's a message available, if there's
a message process it otherwise sleep for a bit and repeat
the loop. The "sleep for a bit" part is what this module's
all about. In any distributed system it's critical not to
get components that operate with this style don't consistently
repeat the same steps at the same time. You want to have lots
of components running thier while loops, reading from queues
at different points in time. You don't want the reads happening
at the same time. With enough components reading and processing
messages the overall system will feel very responsive."""

import logging
import random
import time

_logger = logging.getLogger("CLF_%s" % __name__)


class RRSleeper(object):
    """Instead of repeatedly calling time.sleep() with the
    same # of seconds, construct an instance of ```RRSleeper```
    with a lower and upper bound of a range and, where you would
    have used time.sleep(), have the ```RRSleeper``` instance
    choose a random number of seconds in the range.

    FYI - RR = Random Range"""

    def __init__(self, min_num_secs_to_sleep, max_num_secs_to_sleep):
        """Constructor."""
        object.__init__(self)
        self._min_num_secs_to_sleep = min(
            min_num_secs_to_sleep,
            max_num_secs_to_sleep)
        self._max_num_secs_to_sleep = max(
            min_num_secs_to_sleep,
            max_num_secs_to_sleep)

    def sleep(self):
        """Returns the number of seconds slept."""
        num_secs_to_sleep = random.uniform(
            self._min_num_secs_to_sleep,
            self._max_num_secs_to_sleep)
        num_secs_to_sleep = round(num_secs_to_sleep * 10) / 10
        _logger.info(
            "Sleeping for %.1f (%.1f,%.1f) seconds",
            num_secs_to_sleep,
            self._min_num_secs_to_sleep,
            self._max_num_secs_to_sleep)
        time.sleep(num_secs_to_sleep)
        return num_secs_to_sleep
