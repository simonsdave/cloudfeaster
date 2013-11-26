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

    @classmethod
    def create_repo(cls, repo_name):
        """If the spider repo doesn't exist create it.
        Returns an instance of ```SpiderRepo``` on success
        otherwise ```None```."""
        _logger.info("Attempting to create spider repo '%s'", repo_name)

        conn = S3Connection()
        s3_bucket = conn.lookup(repo_name)
        if not s3_bucket:
            s3_bucket = conn.create_bucket(
                repo_name,
                location=boto.s3.connection.Location.DEFAULT,
                policy='public-read')
            _logger.info(
                "Created bucket '%s' for spider repo",
                repo_name)

            s3_bucket.configure_versioning(True)
            _logger.info(
                "Configured versioning on bucket '%s'",
                repo_name)

            key = s3_bucket.new_key(_magic_key_name)
            key.content_type = "text/plain"
            key.set_contents_from_string("", policy="public-read")
            _logger.info(
                "Created magic key '%s' for spider repo '%s'",
                key.name,
                repo_name)

        return cls(s3_bucket)

    @classmethod
    def get_repo(cls, repo_name):
        """Return a ```SpiderRepo``` if one called ```repo_name```
        exists otherwise return ```None```."""
        conn = S3Connection()
        s3_bucket = conn.lookup(repo_name)
        return cls(s3_bucket) if s3_bucket else None

    def __init__(self, s3_bucket):
        """Constructor."""
        object.__init__(self)
        self._s3_bucket = s3_bucket

    def __str__(self):
        """Returns a string representation of self."""
        return self._s3_bucket.name

    def contents(self):
        """If the spider repo exists delete it.
        Returns ```True``` on success otherwise ```False```."""
        _logger.info("Attempting to determine contents of repo '%s'", self)
        rv = ["%s (%s)" % (key.name, key.version_id)
            for key in self._s3_bucket.get_all_versions()]
        return rv

    def delete(self):
        """If the spider repo exists delete it.
        Returns ```True``` on success otherwise ```False```."""
        _logger.info("Attempting to delete spider repo '%s'", self)
        for version in self._s3_bucket.get_all_versions():
            _logger.info(
                "Deleting '%s (%s)' from spider repo '%s'",
                version.name,
                version.version_id,
                self)
            self._s3_bucket.delete_key(version.name, version_id=version.version_id)
        self._s3_bucket.delete()
        _logger.info("Deleted spider repo '%s'", self)
