"""..."""

import logging

from cmdutil import create_command_to_function_dict
from clf.util.queues import Queue


_logger = logging.getLogger("CLF_%s" % __name__)


command_names = ["q", "queue"]


def doit(usage_func, args):

    if not len(args):
        usage_func("%s [list|create|delete|read] ..." % command_names[0])

    commands = {}
    commands.update(create_command_to_function_dict(["c", "create"], _create))
    commands.update(create_command_to_function_dict(["d", "delete", "rm", "del"], _delete))
    commands.update(create_command_to_function_dict(["l", "ls", "list"], _list))
    commands.update(create_command_to_function_dict(["r", "read"], _read))

    command = commands.get(args[0].strip().lower(), None)
    if not command:
        usage_func("%s [create|delete|list] ..." % command_names[0])

    command(usage_func, args[1:])


def _create(usage_func, args):
    if 1 != len(args):
        usage_func("%s create <queue-name>" % command_names[0])
    queue_name = args[0]
    queue = Queue.get_queue(queue_name)
    if queue:
        print "'%s' already exists" % queue
    else:
        queue = Queue.create_queue(queue_name)
        print "Created '%s'" % queue


def _delete(usage_func, args):
    if 1 != len(args):
        usage_func("%s delete <queue-name>" % command_names[0])
    queue_name = args[0]
    queue = Queue.get_queue(queue_name)
    if queue:
        queue.delete()
        print "Deleted '%s'" % queue_name
    else:
        print "'%s' does not exist" % queue_name


def _list(usage_func, args):
    if 0 != len(args):
        usage_func("%s list" % command_names[0])
    for queue in Queue.get_all_queues():
        print "%s (%d)" % (queue, queue.count())


def _read(usage_func, args):
    if 1 != len(args):
        usage_func("%s read <queue-name>" % command_names[0])

    queue_name = args[0]
    queue = Queue.get_queue(queue_name)
    if not queue:
        _logger.error("queue '%s' does not exist", queue_name)
        return

    message = queue.read_message()
    if message:
        print message
        message.delete()
