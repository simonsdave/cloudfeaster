"""This module contains unit tests for the ```spider_repo``` module."""

import uuid
import unittest

import mock

from clf.spider_repo import SpiderRepo

class TestSpiderRepo(unittest.TestCase):

    def test_ctr_correctly_sets_name_arg(self):
        spider_repo_name = str(uuid.uuid4())
        mock_s3_bucket = mock.Mock()
        mock_s3_bucket.name = spider_repo_name
        spider_repo = SpiderRepo(mock_s3_bucket)
        self.assertEqual(mock_s3_bucket, spider_repo._s3_bucket)

    def test__str__functions_correctly(self):
        spider_repo_name = str(uuid.uuid4())
        mock_s3_bucket = mock.Mock()
        mock_s3_bucket.name = spider_repo_name
        spider_repo = SpiderRepo(mock_s3_bucket)
        self.assertEqual(spider_repo_name, str(spider_repo))
