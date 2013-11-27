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

    _tag_name = "clf"
    _tag_value = "801dbe4659a641739cbe94fcf0baab03"

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

            tag_set = boto.s3.tagging.TagSet()
            tag_set.add_tag(
                cls._tag_name,
                cls._tag_value)
            tag = boto.s3.tagging.Tags()
            tag.add_tag_set(tag_set)
            s3_bucket.set_tags(tag)
            _logger.info(
                "Created tag key/value pair '%s'/'%s' for spider repo '%s'",
                cls._tag_name,
                cls._tag_value,                
                repo_name)

        return cls(s3_bucket)

    @classmethod
    def get_repo(cls, repo_name):
        """Return a ```SpiderRepo``` if one called ```repo_name```
        exists otherwise return ```None```."""
        conn = S3Connection()
        s3_bucket = conn.lookup(repo_name)
        return cls(s3_bucket) if s3_bucket else None

    @classmethod
    def get_all_repos(cls):
        """Return a list of ```SpiderRepo``` instances."""
        def is_sr(bucket):
            try:
                tags = bucket.get_tags()
            except:
                return False
            for tag_set in tags:
                if 1 == len(tag_set):
                    tag = tag_set[0]
                    if (tag.key == cls._tag_name) and (tag.value == cls._tag_value):
                        return True
            return False
                    
        conn = S3Connection()
        all_buckets = conn.get_all_buckets()
        rv = [cls(s3_bucket) for s3_bucket in all_buckets if is_sr(s3_bucket)]
        return rv

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
