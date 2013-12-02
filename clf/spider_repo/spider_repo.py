"""This module contains the ```SpiderRepo``` class which
provides a client interface to the spider repo."""

import logging
import os

import boto
from boto.s3.connection import S3Connection


_logger = logging.getLogger("CLF_%s" % __name__)


class SpiderRepo(object):
    """The spider repo is realized as an S3 bucket.
    This class provides an API for the spider repo
    and executes the S3 operations to implement the
    spider repo API."""

    """```_bucket_name_prefix``` is prepended to
    a repo name to create a bucket name."""
    _bucket_name_prefix = "clf_sr_"

    @classmethod
    def _bucket_name(cls, repo_name):
        """Given a repo name ```repo_name``` create a bucket name."""
        return "%s%s" % (cls._bucket_name_prefix, repo_name)

    @classmethod
    def create_repo(cls, repo_name):
        """If the spider repo doesn't exist create it.
        Returns an instance of ```SpiderRepo``` on success
        otherwise ```None```."""
        _logger.info("Attempting to create spider repo '%s'", repo_name)

        conn = S3Connection()
        bucket = conn.lookup(repo_name)
        if not bucket:
            bucket_name = cls._bucket_name(repo_name)
            _logger.info(
                "Spider repo '%s' bucket name '%s'",
                repo_name,
                bucket_name)

            # :TODO: policy should be figured out - ideal = one set of
            # credentials can edit/admin (ie used by clf cli) and a second
            # set of credentials can only read (ie used by spider host).
            bucket = conn.create_bucket(
                bucket_name,
                location=boto.s3.connection.Location.DEFAULT,
                policy="private")
            _logger.info(
                "Created bucket '%s' for spider repo '%s'",
                bucket_name,
                repo_name)

        return cls(bucket)

    @classmethod
    def get_repo(cls, repo_name):
        """Return a ```SpiderRepo``` if one called ```repo_name```
        exists otherwise return ```None```."""
        conn = S3Connection()
        bucket_name = cls._bucket_name(repo_name)
        bucket = conn.lookup(bucket_name)
        return cls(bucket) if bucket else None

    @classmethod
    def get_all_repos(cls):
        """Returns a list of ```SpiderRepo``` instances."""
        conn = S3Connection()
        all_buckets = conn.get_all_buckets()
        bucket_name_prefix = cls._bucket_name_prefix
        is_repo = lambda bucket: bucket.name.startswith(bucket_name_prefix)
        rv = [cls(bucket) for bucket in all_buckets if is_repo(bucket)]
        return rv

    def __init__(self, bucket):
        """Constructor."""
        object.__init__(self)
        self._bucket = bucket

    def __str__(self):
        """Returns a string representation of self."""
        return self._bucket.name[len(type(self)._bucket_name_prefix):]

    def spiders(self):
        """If the spider repo exists delete it.
        Returns ```True``` on success otherwise ```False```."""
        _logger.info("Attempting to determine contents of repo '%s'", self)
        return [key.name for key in self._bucket.get_all_keys()]

    def delete(self):
        """If the spider repo exists delete it.
        Returns ```True``` on success otherwise ```False```."""
        _logger.info("Attempting to delete spider repo '%s'", self)
        for key in self._bucket.get_all_versions():
            _logger.info(
                "Deleting '%s (%s)' from spider repo '%s'",
                key.name,
                key.version_id,
                self)
            self._bucket.delete_key(
                key.name,
                version_id=key.version_id)
        self._bucket.delete()
        _logger.info("Deleted spider repo '%s'", self)

    def upload_spider(self, filename):
        """Upload a spider's source code to the spider repo.
        ```filename``` contains the spider's source code.
        returns ```True``` on success and ```False```
        on failure."""
        spider_name = os.path.splitext(os.path.basename(filename))[0]
        key = self._bucket.new_key(spider_name)
        # :TODO: figure out how to set content type
        # key.content_type = "application/x-python"
        # :TODO: see above comments on policy
        with open(filename, "r") as fp:
            key.set_contents_from_file(fp, policy="private")
        return True
