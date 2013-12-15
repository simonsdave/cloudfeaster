"""..."""

import imp
import inspect
import logging
import os
import shutil
import tempfile

import sys

from clf.spider import Spider
from remote_spider_repo import RemoteSpiderRepo


_logger = logging.getLogger("CLF_%s" % __name__)


class LocalSpiderRepo(object):

    _parent_spider_module_name = "801dbe4659a641739cbe94fcf0baab03"

    def __init__(self, remote_spider_repo_name):
        object.__init__(self)

        self._local_spider_repo_directory_name = None
        self._remote_spider_repo_name = remote_spider_repo_name
        self._remote_spider_repo = None

    def __enter__(self):
        self._remote_spider_repo = RemoteSpiderRepo.get_repo(
            self._remote_spider_repo_name)
        if self._remote_spider_repo is None:
            return self

        # this odd little section of code is designed to eliminate a
        # warning that appears
        # Parent module '801dbe4659a641739cbe94fcf0baab03' not found while handling absolute import
        self._local_spider_repo_directory_name = tempfile.mkdtemp()

        init_dot_py_filename = os.path.join(
            self._local_spider_repo_directory_name,
            "__init__.py")
        with open(init_dot_py_filename, "w") as source_code_file:
            source_code_file.write("")
        parent_spider_module = imp.load_source(
            # :TODO: maybe module name sb temp file's base name?
            type(self)._parent_spider_module_name,
            init_dot_py_filename)

        return self

    def __exit__(self, type, value, traceback):
        if self._remote_spider_repo:
            self._remote_spider_repo = None
        if self._local_spider_repo_directory_name:
            if os.path.exists(self._local_spider_repo_directory_name):
                try:
                    shutil.rmtree(self._local_spider_repo_directory_name)
                except Exception as ex:
                    _logger.error(
                        "Error removing local spider repo directory '%s' - %s",
                        self._local_spider_repo_directory_name,
                        ex)
            self._local_spider_repo_directory_name = None
            
    def __str__(self):
        return self._remote_spider_repo_name

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

        spider_module_name = "%s.%s" % (type(self)._parent_spider_module_name, spider_name)
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
