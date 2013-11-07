"""..."""

import logging

import boto.sqs.connection

from rrsleeper import RRSleeper


_logger = logging.getLogger("CLF_%s" % __name__)


class Pumper(object):

    def __init__(
        self,
        request_queue_name,
        response_queue_name,
        min_num_secs_to_sleep,
        max_num_secs_to_sleep):

        object.__init__(self)

        self._request_queue_name = request_queue_name
        self._response_queue_name = response_queue_name
        self._min_num_secs_to_sleep = min_num_secs_to_sleep
        self._max_num_secs_to_sleep = max_num_secs_to_sleep

        self._done = False

    def pump(self):

        sqs_conn = boto.sqs.connection.SQSConnection()

        request_queue = sqs_conn.get_queue(self._request_queue_name)
        if not request_queue:
            return

        response_queue = sqs_conn.get_queue(self._response_queue_name)
        if not response_queue:
            return

        rr_sleeper = RRSleeper(
            self._min_num_secs_to_sleep,
            self._max_num_secs_to_sleep)

        while not self._done:

            _logger.info(
                "Reading reqs from queue '%s'",
                request_queue)

            messages = request_queue.get_messages(num_messages=1)
            _logger.info(
                "Read %d messages from queue '%s'",
                len(messages),
                request_queue)
            if len(messages):
                message = messages[0]
                try:
                    pass
                finally:
                    request_queue.delete_message(message)
            else:
                rr_sleeper.sleep()
