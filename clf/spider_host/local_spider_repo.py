"""..."""

import imp
import inspect
import os
import logging
import tempfile

import sys

from clf.spider import Spider
from clf.spider_repo.spider_repo import SpiderRepo


_logger = logging.getLogger("CLF_%s" % __name__)


class LocalSpiderRepo(object):

    def __init__(self, remote_spider_repo_name):
        
        object.__init__(self)

        self._local_spider_repo_directory_name = tempfile.mkdtemp()
        self._remote_spider_repo = SpiderRepo.get_repo(remote_spider_repo_name)

    def __nonzero__(self):
        return self._remote_spider_repo is not None

    def get_spider_class(self, spider_name):
        if not self:
            return None

        source_code = self._remote_spider_repo.download_spider(spider_name)
        if not source_code:
            return None

        # :TODO: maybe just write to temp file
        # conside scenario of running out of temp file space but spider names are finite
        source_code_filename = os.path.join(
            self._local_spider_repo_directory_name,
            spider_name)
        with open(source_code_filename, "w") as source_code_file:
            source_code_file.write(source_code)

        spider_module_name = "clf.spider_host.spider.%s" % spider_name
        spider_module = imp.load_source(
            # :TODO: maybe module name sb temp file's base name?
            spider_module_name,
            source_code_filename)
        if not spider_module:
            return None

        spider_class = None
        spider_module_members = inspect.getmembers(
            spider_module,
            inspect.isclass)
        for _, potential_spider_class in spider_module_members:
            if issubclass(potential_spider_class, Spider):
                spider_class = potential_spider_class
                break

        return spider_class
