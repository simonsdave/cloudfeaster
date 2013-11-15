"""This module contains the ```SpiderRepo``` class which
provides a client interface to the spider repo."""

import logging


_logger = logging.getLogger("CLF_%s" % __name__)


class SpiderRepo(object):
    """..."""

    def __init__(self, name):
        """Constructor."""
        object.__init__(self)
        self.name = name

    def __str__(self):
        """Returns a string representation of self."""
        return self.name

    def exists(self):
        """Returns ```True``` if spider repo exists otherwise
        returns ```False```."""
        try:
            conn = boto.s3.connection.S3Connection()
            bucket = conn.get_bucket(bucket_name)
        except:
            return False

        return True

    def create(self):
        """If the spider repo doesn't exist create it.
        Returns ```True``` on success otherwise ```False```."""
        logger.info("Attempting to spider repo '%s'", self)
        if self.exists():
            return False
        try:
            conn = boto.s3.connection.S3Connection()
            bucket = conn.create_bucket(
                bucket_name,
                location=boto.s3.connection.Location.DEFAULT,
                policy='public-read')
            logger.info("Created spider repo '%s'", self)
        except Exception as ex:
            logger.error("Spider repo create error '%s' - %s", self, str(ex))
            return False
        return True
