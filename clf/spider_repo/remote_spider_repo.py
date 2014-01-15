"""This module contains the ```RemoteSpiderRepo``` class which
provides a client interface to the spider repo."""

import logging
import os

import boto
from boto.s3.connection import S3Connection


_logger = logging.getLogger("CLF_%s" % __name__)


class RemoteSpiderRepo(object):
    """The remote spider repo is realized as an S3 bucket.
    This class provides an API for the remote spider repo
    and executes the S3 operations to implement the
    remote spider repo API."""

    """```_bucket_name_prefix``` is prepended to
    a repo name to create a bucket name."""
    _bucket_name_prefix = "clf_sr_"

    """```_content_type``` defines the content type for
    spider in the remote spider repo."""
    _content_type = "text/x-python"

    @classmethod
    def _bucket_name(cls, remote_repo_name):
        """Given a repo name ```remote_repo_name``` create a bucket name."""
        return "%s%s" % (cls._bucket_name_prefix, remote_repo_name)

    @classmethod
    def create_repo(cls, remote_repo_name):
        """If the remote spider repo doesn't exist create it.
        Returns an instance of ```RemoteSpiderRepo``` on success
        otherwise ```None```."""
        _logger.info(
            "Attempting to create remote spider repo '%s'",
            remote_repo_name)

        bucket_name = cls._bucket_name(remote_repo_name)
        _logger.info(
            "Remote spider repo '%s's bucket name is '%s'",
            remote_repo_name,
            bucket_name)

        conn = S3Connection()
        bucket = conn.lookup(bucket_name)
        if not bucket:
            # :TODO: policy should be figured out - ideal = one set of
            # credentials can edit/admin (ie used by clf cli) and a second
            # set of credentials can only read (ie used by spider host).
            bucket = conn.create_bucket(
                bucket_name,
                location=boto.s3.connection.Location.DEFAULT,
                policy="private")
            _logger.info(
                "Created bucket '%s' for remote spider repo '%s'",
                bucket_name,
                remote_repo_name)

        return cls(bucket)

    @classmethod
    def get_repo(cls, remote_repo_name):
        """Return a ```RemoteSpiderRepo``` if one called ```remote_repo_name```
        exists otherwise return ```None```."""
        conn = S3Connection()
        bucket_name = cls._bucket_name(remote_repo_name)
        bucket = conn.lookup(bucket_name)
        return cls(bucket) if bucket else None

    @classmethod
    def _is_sr(cls, bucket):
        """Returns ```True``` if ```bucket``` is a spider repo otherwise
        returns ```False```."""
        return bucket.name.startswith(cls._bucket_name_prefix)

    @classmethod
    def get_all_repos(cls):
        """Returns a list of ```RemoteSpiderRepo``` instances."""
        _logger.info("Searching for remote spider repos")
        conn = S3Connection()
        all_buckets = conn.get_all_buckets()
        rv = [cls(bucket) for bucket in all_buckets if cls._is_sr(bucket)]
        _logger.info("Found %d remote spider repos", len(rv))
        return rv

    def __init__(self, bucket):
        """Constructor."""
        object.__init__(self)
        self._bucket = bucket

    def __str__(self):
        """Returns a string representation of self."""
        return self._bucket.name[len(type(self)._bucket_name_prefix):]

    def spiders(self):
        """Return a list of the names of all spiders in the remote repo."""
        _logger.info("Finding spiders in remote spider repo '%s'", self)
        rv = [key.name for key in self._bucket.get_all_keys()]
        _logger.info("Remote spider repo '%s' has %d spiders", self, len(rv))
        return rv

    def delete(self):
        """If the remote spider repo exists delete it.
        Returns ```True``` on success otherwise ```False```."""
        _logger.info("Attempting to delete remote spider repo '%s'", self)
        for key in self._bucket.get_all_versions():
            _logger.info(
                "Deleting '%s (%s)' from remote spider repo '%s'",
                key.name,
                key.version_id,
                self)
            self._bucket.delete_key(
                key.name,
                version_id=key.version_id)
        self._bucket.delete()
        _logger.info("Deleted spider remote repo '%s'", self)

    def upload_spider(self, filename):
        """Upload a spider's source code to the remote spider repo.
        ```filename``` contains the spider's source code.
        returns ```True``` on success and ```False```
        on failure."""

        if not os.path.exists(filename):
            fmt = (
                "Attempt to upload '%s' to spider repo '%s' failed "
                "because '%s' does not exist"
            )
            _logger.error(fmt, filename, self, filename)
            return False

        # :TODO: do some basic validation on the spider:
        #
        # 1/ make sure there's a spider class
        # 2/ the spider class should contain a crawl method
        # 3/ the spider class should contain metadata which
        # describes (i) the site being crawled (ii) the crawl
        # args (think enough detail that a UI could be dynamically
        # constructed) - the metadata is a json document
        #
        # to do all of the above add a new fuction to clf.spider
        # module which accepts a module as argument

        spider_name = os.path.splitext(os.path.basename(filename))[0]
        key = self._bucket.new_key(spider_name)
        # :TODO: see above comments on policy
        key.set_metadata("Content-Type", type(self)._content_type)
        with open(filename, "r") as fp:
            key.set_contents_from_file(fp, policy="private")

        return True

    def download_spider(self, spider_name):
        """Attempt to download and return the source code for
        spider called ```spider_name```. None is returned if the
        spider's source code can't be found or if an error occurs."""
        fmt = (
            "Attempting to download source code for spider '%s' "
            "from remote spider repo '%s'"
        )
        _logger.info(fmt, spider_name, self)

        key = self._bucket.get_key(spider_name)
        if not key:
            _logger.info(
                "Could not find spider '%s' in remote spider repo '%s'",
                spider_name,
                self)
            return None

        _logger.info(
            "Located entry for spider '%s' in remote spider repo '%s'",
            spider_name,
            self)

        if key.content_type != type(self)._content_type:
            fmt = (
                "Spider '%s' in remote spider repo '%s' "
                "has content type '%s' but expected '%s'"
            )
            _logger.info(
                fmt,
                spider_name,
                self,
                key.content_type,
                type(self)._content_type)
            return None

        source_code = key.get_contents_as_string()
        _logger.info(
            "Got '%s's source code (%d bytes) from remote spider repo '%s'",
            spider_name,
            len(source_code),
            self)

        return source_code
