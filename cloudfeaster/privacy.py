"""This module exists as a place to centralize functionality and
configuration related to privacy.
"""

import hashlib
import logging


class RedactingFormatter(object):
    """
    Credits - this formatter was heavily inspired by https://relaxdiego.com/2014/07/logging-in-python.html
    """

    @classmethod
    def install_for_all_handlers(self, crawl_args):
        # :TODO: can this be configured when configuring logging
        # this is inspired by https://gist.github.com/acdha/9238791
        for handler in logging.root.handlers:
            handler.setFormatter(self(handler.formatter, crawl_args))

    def __init__(self, original_formatter, crawl_args):
        self.original_formatter = original_formatter

        self._patterns_and_replacements = []
        for crawl_arg in crawl_args:
            replacement = hash_crawl_arg(crawl_arg)
            self._patterns_and_replacements.append((crawl_arg, replacement))

            pattern = '"' + '", "'.join(crawl_arg) + '"'
            replacement = '"' + '", "'.join(hash_crawl_arg(crawl_arg)) + '"'
            self._patterns_and_replacements.append((pattern, replacement))

    def format(self, record):
        msg = self.original_formatter.format(record)
        for (pattern, replacement) in self._patterns_and_replacements:
            msg = msg.replace(pattern, replacement)
        return msg

    def __getattr__(self, attr):
        return getattr(self.original_formatter, attr)


class RedactingFilter(logging.Filter):

    def __init__(self, crawl_args):
        super(RedactingFilter, self).__init__()

        self._patterns_and_replacements = []
        for crawl_arg in crawl_args:
            replacement = hash_crawl_arg(crawl_arg)
            self._patterns_and_replacements.append((crawl_arg, replacement))

            pattern = '"' + '", "'.join(crawl_arg) + '"'
            replacement = '"' + '", "'.join(hash_crawl_arg(crawl_arg)) + '"'
            self._patterns_and_replacements.append((pattern, replacement))

    def filter(self, record):
        record.msg = self.redact(record.msg)
        if isinstance(record.args, dict):
            for k in record.args.keys():
                record.args[k] = self._redact(record.args[k])
        else:
            record.args = tuple(self._redact(arg) for arg in record.args)
        return True

    def _redact(self, msg):
        msg = None
        # isinstance(msg, basestring) and msg or str(msg)
        for (pattern, replacement) in self._patterns_and_replacements:
            msg = msg.replace(pattern, replacement)
        return msg


def hash_crawl_arg(crawl_arg):
    """Take a crawl argument (ie. an identifying or authenticating factor)
    and create a hash. Hash will have the form <hash function name>:<hash digest>.
    """
    hash = hashlib.sha256(str(crawl_arg).encode('utf-8'))
    return '{hash_name}:{hash_digest}'.format(hash_name=hash.name, hash_digest=hash.hexdigest())
