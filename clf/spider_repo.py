"""This module contains the ```SpiderRepo``` class which
provides a client interface to the spider repo."""

import logging

import boto
from boto.s3.connection import S3Connection


_logger = logging.getLogger("CLF_%s" % __name__)


_magic_key_name = "801dbe4659a641739cbe94fcf0baab03"


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
            key = bucket.new_key(_magic_key_name)
            key.content_type = "text/plain"
            key.set_contents_from_string("", policy="public-read")
            _logger.info(
                "Created magic key '%s' for spider repo '%s'",
                key.name,
                self)
        except Exception as ex:
            _logger.error("Spider repo create error '%s' - %s", self, str(ex))
            return False
        return True

    def contents(self):
        """If the spider repo exists delete it.
        Returns ```True``` on success otherwise ```False```."""
        _logger.info("Attempting to determine contents of repo '%s'", self)
        try:
            conn = S3Connection()
            bucket = conn.lookup(self.name)
            if not bucket:
                _logger.info(
                    "Can't get contents of non-existant spider repo '%s'",
                    self)
                return None
            return ["%s (%s)" % (key.name, key.version_id) for key in bucket.get_all_versions()]
        except Exception as ex:
            _logger.error("Can't get contents of spider repo '%s' - %s", self, str(ex))
            return None

    def delete(self):
        """If the spider repo exists delete it.
        Returns ```True``` on success otherwise ```False```."""
        _logger.info("Attempting to delete spider repo '%s'", self)
        try:
            conn = S3Connection()
            bucket = conn.lookup(self.name)
            if not bucket
                _logger.info("Can't delete non-existant spider repo '%s'", self)
                return False
            for version in bucket.get_all_versions():
                _logger.info(
                    "Deleting '%s (%s)' from spider repo '%s'",
                    version.name,
                    version.version_id,
                    self)
                bucket.delete_key(version.name, version_id=version.version_id)
            bucket.delete()
            _logger.info("Deleted spider repo '%s'", self)
            return True
        except Exception as ex:
            _logger.error("Spider repo delete error '%s' - %s", self, str(ex))
            return False
