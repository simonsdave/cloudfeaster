"""This module contains tests for local_spider_repo module."""

import os
import shutil
import sys
import unittest
import uuid

import mock

from clf.spider_repo.local_spider_repo import LocalSpiderRepo


class TestLocalSpiderRepo(unittest.TestCase):

    def test_ctr(self):
        remote_spider_repo_name = str(uuid.uuid4())
        lsr = LocalSpiderRepo(remote_spider_repo_name)
        self.assertEqual(
            lsr._remote_spider_repo_name,
            remote_spider_repo_name)
        self.assertIsNone(lsr._local_spider_repo_directory_name)
        self.assertIsNone(lsr._remote_spider_repo)

    def test_context_manager_and_remote_spider_repo_not_found(self):
        remote_spider_repo_name = str(uuid.uuid4())
        mock_get_repo_method = mock.Mock(return_value=None)

        name_of_method_to_patch = "clf.spider_repo.spider_repo.SpiderRepo.get_repo"
        with mock.patch(name_of_method_to_patch, mock_get_repo_method):
            with LocalSpiderRepo(remote_spider_repo_name) as lsr:
                self.assertIsNotNone(lsr)
                self.assertIsNone(lsr._remote_spider_repo)
                self.assertIsNone(lsr._local_spider_repo_directory_name)

        mock_get_repo_method.assert_called_once_with(remote_spider_repo_name)

    def test_context_manager_and_local_spider_repo_directory_all_good(self):
        remote_spider_repo_name = str(uuid.uuid4())
        remote_spider_repo = mock.Mock()
        mock_get_repo_method = mock.Mock(return_value=remote_spider_repo)

        name_of_method_to_patch = "clf.spider_repo.spider_repo.SpiderRepo.get_repo"
        with mock.patch(name_of_method_to_patch, mock_get_repo_method):
            with LocalSpiderRepo(remote_spider_repo_name) as lsr:
                self.assertIsNotNone(lsr)

                self.assertEqual(lsr._remote_spider_repo, remote_spider_repo)

                self.assertIsNotNone(lsr._local_spider_repo_directory_name)
                self.assertTrue(os.path.exists(lsr._local_spider_repo_directory_name))
                local_spider_repo_directory_name = lsr._local_spider_repo_directory_name

                init_dot_py_filename = os.path.join(
                    lsr._local_spider_repo_directory_name,
                    "__init__.py")
                self.assertTrue(os.path.exists(init_dot_py_filename))
                statinfo = os.stat(init_dot_py_filename)
                self.assertEqual(0, statinfo.st_size)

                self.assertIn(type(lsr)._parent_spider_module_name, sys.modules)

        self.assertIsNone(lsr._local_spider_repo_directory_name)
        self.assertFalse(os.path.exists(local_spider_repo_directory_name))

        self.assertIsNone(lsr._remote_spider_repo)

        mock_get_repo_method.assert_called_once_with(remote_spider_repo_name)

    def test_context_manager_and_local_spider_repo_directory_error_on_cleanup(self):
        remote_spider_repo = mock.Mock()
        mock_get_repo_method = mock.Mock(return_value=remote_spider_repo)

        name_of_method_to_patch = "clf.spider_repo.spider_repo.SpiderRepo.get_repo"
        with mock.patch(name_of_method_to_patch, mock_get_repo_method):
            shutil_rmtree_function_mock = mock.Mock(side_effect=Exception("something"))
            with mock.patch("shutil.rmtree", shutil_rmtree_function_mock):
                with LocalSpiderRepo(str(uuid.uuid4())) as lsr:
                    self.assertIsNotNone(lsr)
                    self.assertIsNotNone(lsr._local_spider_repo_directory_name)
                    local_spider_repo_directory_name = lsr._local_spider_repo_directory_name
                    self.assertTrue(os.path.exists(local_spider_repo_directory_name))
            shutil_rmtree_function_mock.called_once_with(local_spider_repo_directory_name)

        self.assertTrue(os.path.exists(local_spider_repo_directory_name))
        shutil.rmtree(local_spider_repo_directory_name)

    def test_str(self):
        remote_spider_repo_name = str(uuid.uuid4())
        lsr = LocalSpiderRepo(remote_spider_repo_name)
        self.assertEqual(remote_spider_repo_name, str(lsr))

    def test_nonzero_true(self):
        lsr = LocalSpiderRepo(str(uuid.uuid4()))
        self.assertFalse(lsr)

    def test_nonzero_false(self):
        mock_get_repo_method = mock.Mock(return_value=mock.Mock())
        name_of_method_to_patch = "clf.spider_repo.spider_repo.SpiderRepo.get_repo"
        with mock.patch(name_of_method_to_patch, mock_get_repo_method):
            with LocalSpiderRepo(str(uuid.uuid4())) as lsr:
                self.assertIsNotNone(lsr)
                self.assertTrue(lsr)
