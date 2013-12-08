"""This module contains unit tests for the ```spider_repo``` module."""

import binascii
import os
import subprocess
import tempfile
import uuid
import unittest

from nose.plugins.attrib import attr
import mock

from clf.spider_repo.spider_repo import SpiderRepo

class TestSpiderRepoTests(unittest.TestCase):

    def test_ctr_correctly_sets_name_arg(self):
        repo_name = str(uuid.uuid4())
        mock_bucket = mock.Mock()
        spider_repo = SpiderRepo(mock_bucket)
        self.assertEqual(mock_bucket, spider_repo._bucket)

    def test__str__functions_correctly(self):
        repo_name = str(uuid.uuid4())
        mock_bucket = mock.Mock()
        mock_bucket.name = "%s%s" % (SpiderRepo._bucket_name_prefix, repo_name)
        spider_repo = SpiderRepo(mock_bucket)
        self.assertEqual(repo_name, str(spider_repo))

    def _subprocess_call(self, *args):
        with open(os.devnull, "w") as dev_null:
            return subprocess.call(*args, stdout=dev_null, stderr=dev_null)

    def _does_repo_exist(self, repo_name):
        subprocess_call_args = [
            "aws",
            "s3",
            "ls",
            "s3://%s%s" % (SpiderRepo._bucket_name_prefix, repo_name)]
        return 0 == self._subprocess_call(subprocess_call_args)

    @attr('integration')
    def test_create_get_and_delete_repo(self):
        repo_name = binascii.b2a_hex(os.urandom(8))

        self.assertFalse(self._does_repo_exist(repo_name))
        spider_repo = SpiderRepo.get_repo(repo_name)
        self.assertIsNone(spider_repo)

        spider_repo = SpiderRepo.create_repo(repo_name)
        self.assertIsNotNone(spider_repo)
        self.assertTrue(self._does_repo_exist(repo_name))
        self.assertIsNotNone(SpiderRepo.get_repo(repo_name))

        spider_repo.delete()
        self.assertFalse(self._does_repo_exist(repo_name))
        spider_repo = SpiderRepo.get_repo(repo_name)
        self.assertIsNone(spider_repo)

    def _create_temp_spider_source_file(self, directory_name, file_name):
        source_code_filename = os.path.join(directory_name, file_name)
        with open(source_code_filename, "w") as source_file:
            source_file.write("#" * 80)
        return source_code_filename

    @attr('integration')
    def test_upload_spider_and_spiders(self):
        repo_name = binascii.b2a_hex(os.urandom(8))

        spider_repo = SpiderRepo.create_repo(repo_name)
        self.assertIsNotNone(spider_repo)
        try:
            spiders = spider_repo.spiders()
            self.assertEqual(0, len(spiders))

            directory_name = tempfile.mkdtemp()

            source_code_filename_1 = self._create_temp_spider_source_file(
                directory_name,
                "one.py")

            source_code_filename_2 = self._create_temp_spider_source_file(
                directory_name,
                "two.py")

            source_code_filename_3 = self._create_temp_spider_source_file(
                directory_name,
                "three.py")

            spider_repo.upload_spider(source_code_filename_1)
            spiders = spider_repo.spiders()
            self.assertEqual(1, len(spiders))

            spider_repo.upload_spider(source_code_filename_2)
            spiders = spider_repo.spiders()
            self.assertEqual(2, len(spiders))

            spider_repo.upload_spider(source_code_filename_3)
            spiders = spider_repo.spiders()
            self.assertEqual(3, len(spiders))
        finally:
            spider_repo.delete()

    @attr('integration')
    def test_download_spider(self):
        repo_name = binascii.b2a_hex(os.urandom(8))

        spider_repo = SpiderRepo.create_repo(repo_name)
        self.assertIsNotNone(spider_repo)
        try:
            source_code = "#" * 80
            source_code = source_code + '\n'
            source_code = source_code + ("-" * 80)
            spider_name = binascii.b2a_hex(os.urandom(8))
            directory_name = tempfile.mkdtemp()
            source_code_filename = os.path.join(
                directory_name,
                "%s.py" % spider_name)
            with open(source_code_filename, "w") as source_file:
                source_file.write(source_code)

            dl_source_code = spider_repo.download_spider(spider_name)
            self.assertIsNone(dl_source_code)

            rv = spider_repo.upload_spider(source_code_filename)
            self.assertTrue(rv)

            dl_source_code = spider_repo.download_spider(spider_name)
            self.assertIsNotNone(dl_source_code)
            self.assertEqual(dl_source_code, source_code)
        finally:
            spider_repo.delete()