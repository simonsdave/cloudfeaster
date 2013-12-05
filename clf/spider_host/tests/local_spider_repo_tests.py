"""This module contains unit tests for the spider host's
local_spider_repo module."""

import unittest
import uuid

import mock

from clf.spider_host.local_spider_repo import LocalSpiderRepo


class TestLocalSpiderRepo(unittest.TestCase):

    def test_ctr(self):
        """..."""
        mock_get_repo_method = mock.Mock(return_value=None)
        remote_spider_repo_name = str(uuid.uuid4())
        name_of_method_to_patch = "clf.spider_repo.spider_repo.SpiderRepo.get_repo"
        with mock.patch(name_of_method_to_patch, mock_get_repo_method):
            lsr = LocalSpiderRepo(remote_spider_repo_name)
        mock_get_repo_method.assert_called_once_with(remote_spider_repo_name)
