"""..."""

import logging

from clf.spider_repo import SpiderRepo


_logger = logging.getLogger("CLF_%s" % __name__)


command_name = "spider_repo"


def doit(usage_func, args):

    if len(args) < 2:
        usage_func("%s [create|delete|contents] ..." % command_name)
        spider_repo_usage()

    commands = {
        "c": _create,
        "create": _create,
        "d": _delete,
        "rm": _delete,
        "del": _delete,
        "delete": _delete,
        "contents": _contents,
        "ls": _contents,
    }
    command = commands.get(args[0].strip().lower(), None)
    if not command:
        usage_func("%s [create|delete|contents] ..." % command_name)

    command(usage_func, args[1:])


def _create(usage_func, args):
    if 1 != len(args):
        usage_func("%s create <repo-name>" % command_name)
    
    spider_repo = SpiderRepo(args[0])

    if spider_repo.create():
        print "Created spider repo '%s'" % spider_repo
    else:
        _logger.error("Could not create spider repo '%s'", spider_repo)


def _delete(usage_func, args):
    if 1 != len(args):
        usage_func("%s delete <repo-name>" % command_name)

    spider_repo = SpiderRepo(args[0])

    if spider_repo.delete():
        print "Deleted spider repo '%s'" % spider_repo
    else:
        _logger.error("Could not delete spider repo '%s'", spider_repo)


def _contents(usage_func, args):
    if 1 != len(args):
        usage_func("%s contents <repo-name>" % command_name)

    spider_repo = SpiderRepo(args[0])
    contents = spider_repo.contents()
    if contents:
        print "Contents of spider repo '%s'" % spider_repo
        for content in contents:
            print "-- %s" % content
    else:
        _logger.error("Could not get contents of spider repo '%s'", spider_repo)
