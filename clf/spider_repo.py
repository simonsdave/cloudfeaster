"""This module contains the ```SpiderRepo``` class which
provides a client interface to the spider repo."""

import logging

import boto
from boto.s3.connection import S3Connection


_logger = logging.getLogger("CLF_%s" % __name__)


class SpiderRepo(object):
    """The spider repo is realized as an S3 bucket
    with versioning enabled. This class provides an
    API for the spider repo and executes the S3
    operations to implement the spider repo API."""

    def __init__(self, name):
        """Constructor."""
        object.__init__(self)
        self.name = name

    def __str__(self):
        """Returns a string representation of self."""
        return self.name

    def exists(self):
        """Return ```True``` if spider repo exists otherwise
        return ```False```."""
        try:
            conn = S3Connection()
            return conn.lookup(self.name) is not None
        except Exception as ex:
            _logger.error(
                "Error searching for spider repo '%s' - %s",
                self,
                str(ex))
        return False

    def create(self):
        """If the spider repo doesn't exist create it.
        Returns ```True``` on success otherwise ```False```."""
        _logger.info("Attempting to create spider repo '%s'", self)
        if self.exists():
            _logger.info("Can't recreate spider repo '%s'", self)
            return False
        try:
            conn = S3Connection()
            bucket = conn.create_bucket(
                self.name,
                headers={"x-amz-meta-dave": "dave"},
                location=boto.s3.connection.Location.DEFAULT,
                policy='public-read')
            _logger.info("Created spider repo '%s'", self)
            bucket.configure_versioning(True)
            _logger.info("Enabled versioning for spider repo '%s'", self)
        except Exception as ex:
            _logger.error("Spider repo create error '%s' - %s", self, str(ex))
            return False
        return True

    def delete(self):
        """If the spider repo exists delete it.
        Returns ```True``` on success otherwise ```False```."""
        _logger.info("Attempting to delete spider repo '%s'", self)
        if not self.exists():
            _logger.info("Can't delete non-existant spider repo '%s'", self)
            return False
        try:
            conn = S3Connection()
            bucket = conn.get_bucket(self.name)
            for key in bucket.get_all_keys():
                _logger.info(
                    "Deleting '%s' from spider repo '%s'",
                    key.name,
                    self)
                key.delete()
            bucket.delete()
            _logger.info("Deleted spider repo '%s'", self)
        except Exception as ex:
            _logger.error("Spider repo delete error '%s' - %s", self, str(ex))
            return False
        return True
