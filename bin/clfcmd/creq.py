"""This module extends the clf cli so it can manipulate a
crawl request queue."""

import json
import logging

import boto

from cmdutil import create_command_to_function_dict
from clf.spider_host.queues import CrawlRequestQueue
from clf.spider_host.queues import CrawlRequestMessage


_logger = logging.getLogger("CLF_%s" % __name__)


command_names = ["creq"]


def doit(usage_func, args):
    usage_fmt = "%s [ls|c|rm|r|w|we] ..."

    if 0 == len(args):
        usage_func(usage_fmt % command_names[0])

    commands = {}
    commands.update(create_command_to_function_dict(["ls", "list"], _list))
    commands.update(create_command_to_function_dict(["c", "create"], _create))
    commands.update(create_command_to_function_dict(["rm", "remove", "del"], _delete))
    commands.update(create_command_to_function_dict(["r", "read"], _read))
    commands.update(create_command_to_function_dict(["write", "w"], _write))
    commands.update(create_command_to_function_dict(["write_error", "we"], _write_error))

    command = commands.get(args[0].strip().lower(), None)
    if not command:
        usage_func(usage_fmt % command_names[0])

    command(usage_func, args[1:])


def _list(usage_func, args):
    if 0 != len(args):
        usage_func("%s ls" % command_names[0])

    for queue in CrawlRequestQueue.get_all_queues():
        print "%s (%d)" % (queue, queue.count())


def _create(usage_func, args):
    if 1 != len(args):
        usage_func("%s c <queue-name>" % command_names[0])

    queue_name = args[0]

    queue = CrawlRequestQueue.create_queue(queue_name)
    if queue:
        _logger.info("Created queue '%s'", queue)
    else:
        _logger.error("Failed to create queue '%s'", queue_name)


def _delete(usage_func, args):
    if 1 != len(args):
        usage_func("%s rm <queue-name>" % command_names[0])

    queue_name = args[0]

    queue = CrawlRequestQueue.get_queue(queue_name)
    if queue:
        _logger.info("Found queue '%s'", queue)
        queue.delete()
        _logger.info("Deleted queue '%s'", queue)
    else:
        _logger.error("Couldn't find queue '%s'", queue_name)


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


def _read(usage_func, args):
    if 1 != len(args):
        usage_func("%s r <queue-name>" % command_names[0])

    queue_name = args[0]

    queue = CrawlRequestQueue.get_queue(queue_name)
    if queue:
        _logger.info("Found queue '%s'", queue)
        message = queue.read_message()
        if message:
            print json.dumps(message, indent=4)
            message.delete()
            _logger.info("Deleted message '%s'", message)
    else:
        _logger.error("Couldn't find queue '%s'", queue_name)


def _write_error(usage_func, args):
    if 1 != len(args):
        usage_func("%s write_error <queue-name>" % command_names[0])

    queue_name = args[0]

    sqs_conn = boto.sqs.connection.SQSConnection()
    queue = sqs_conn.get_queue(queue_name)
    if not queue:
        _logger.error("queue '%s' does not exist", queue_name)
        return

    message = boto.sqs.message.Message()
    message.set_body("bindle")

    queue.write(message)
