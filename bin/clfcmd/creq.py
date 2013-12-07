"""..."""

import logging

from cmdutil import create_command_to_function_dict
from clf.spider_host.queues import CrawlRequestQueue
from clf.spider_host.queues import CrawlRequestMessage


_logger = logging.getLogger("CLF_%s" % __name__)


command_names = ["creq"]


def doit(usage_func, args):

    if 0 == len(args):
        usage_func("%s [write|write_error] ..." % command_names[0])

    commands = {}
    commands.update(create_command_to_function_dict(["write", "w"], _write))
    commands.update(create_command_to_function_dict(["write_error", "we"], _write_error))

    command = commands.get(args[0].strip().lower(), None)
    if not command:
        usage_func("%s [write|write_error] ..." % command_names[0])

    command(usage_func, args[1:])


def _write(usage_func, args):
    if len(args) < 2:
        fmt = "%s write <queue-name> <spider-name> <arg1> ... <argN>"
        usage_func(fmt % command_names[0])

    queue_name = args[0]
    spider_name = args[1]
    spider_args = args[2:]

    queue = CrawlRequestQueue.get_queue(queue_name)
    if queue:
        request = CrawlRequestMessage(
            spider_name=spider_name,
            spider_args=spider_args)
        queue.write_message(request)
    else:
        _logger.error("Couldn't find queue '%s'", queue_name)


def _write_error(usage_func, args):
    if 1 != len(args):
        usage_func("%s write_error <queue-name>" % command_names[0])

    queue_name = args[0]

    queue = sqs_conn.get_queue(queue_name)
    if not queue:
        _logger.error("queue '%s' does not exist", queue_name)
        return

    message = boto.sqs.message.Message()
    message.set_body("bindle")

    queue.write(message)
