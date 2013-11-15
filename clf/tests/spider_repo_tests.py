"""This module contains unit tests for the ```spider_repo``` module."""

import uuid
import unittest

from clf.spider_repo import SpiderRepo

class TestSpiderRepo(unittest.TestCase):

    def test_ctr_correctly_sets_name_arg(self):
        spider_repo_name = str(uuid.uuid4())
        spider_repo = SpiderRepo(spider_repo_name)
        self.assertEqual(spider_repo_name, spider_repo.name)

    def test__str__functions_correctly(self):
        spider_repo_name = str(uuid.uuid4())
        spider_repo = SpiderRepo(spider_repo_name)
        self.assertEqual(spider_repo_name, str(spider_repo))
