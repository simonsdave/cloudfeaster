"""..."""

import logging

import boto.sqs.connection

from rrsleeper import RRSleeper


_logger = logging.getLogger("CLF_%s" % __name__)


def pump(
    request_queue_name,
    response_queue_name,
    min_num_secs_to_sleep,
    max_num_secs_to_sleep):

    sqs_conn = boto.sqs.connection.SQSConnection()

    request_queue = sqs_conn.get_queue(request_queue_name)
    if not request_queue:
        return

    response_queue = sqs_conn.get_queue(response_queue_name)
    if not response_queue:
        return

    rr_sleeper = RRSleeper(
        min_num_secs_to_sleep,
        max_num_secs_to_sleep)

    while True:

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
