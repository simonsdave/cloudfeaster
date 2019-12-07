"""This module exists as a place to centralize functionality and
configuration related to privacy.
"""

import hashlib


def hash_spider_arg(spider_arg):
    """Take a spider argument (ie. an identifying or authenticating factor)
    and create a hash. Hash will have the form <hash function name>:<hash digest>.
    """
    hash = hashlib.sha256(str(spider_arg))
    return '{hash_name}:{hash_digest}'.format(hash_name=hash.name, hash_digest=hash.hexdigest())
