from __future__ import print_function
import unittest
from pyfakefs import fake_filesystem
from release_ccharp.apps.common.directory_handling import AppPaths
from release_ccharp.snpseq_paths import SnpseqPathProperties
from tests.unit.utility.fake_os_service import FakeOsService


class AppPathTests(unittest.TestCase):
    def setUp(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "chiasma",
            "exe_file_name_base": "Chiasma",
            "project_root_dir": "Chiasma",
            "confluence_space_key": "CHI",
            "owner": "GitEdvard"
        }
        filesystem = fake_filesystem.FakeFilesystem()
        chiasma_exe = (r'c:\xxx\chiasma\candidates\new-candidate\GitEdvard-chiasma-123\chiasma\bin'
                       r'\release\chiasma.exe')
        filesystem.CreateFile(chiasma_exe)
        branch_provider = FakeBranchProvider()
        path_properties = SnpseqPathProperties(config, "chiasma", None)
        path_properties.branch_provider = branch_provider
        os_service = FakeOsService(filesystem)
        self.os_module = os_service.os_module
        self.app_paths = AppPaths(config, path_properties, os_service)

    def test_find_download_directory__with_one_matching_dir_in_candidate__return_matching_dir(self):
        dirname = self.app_paths.find_download_directory_name()
        self.assertEqual("GitEdvard-chiasma-123", dirname)

    def test_download_dir__with_added_download_dir_according_to_setup__returns_correctly(self):
        dirname = self.app_paths.download_dir
        self.assertEqual(r"c:\xxx\chiasma\candidates\new-candidate\GitEdvard-chiasma-123", dirname)

    def test_validation_dir__with_creation_by_convertion__returns_correctly(self):
        dirname = self.app_paths.validation_dir
        self.assertEqual(r'c:\xxx\chiasma\candidates\new-candidate\validation', dirname)

    def test_production_dir__with_creation_by_convention__returns_correctly(self):
        dirname = self.app_paths.production_dir
        self.assertEqual(r'c:\xxx\chiasma\candidates\new-candidate\production', dirname)

    def test_config_file_name__with_creation_by_convention__returns_correctly(self):
        name = self.app_paths.config_file_name
        self.assertEqual("Chiasma.exe.config", name)

    def test_move_candidates__with_one_file_added_in_bin_release__file_found_in_validation(self):
        project_root = r'c:\xxx\chiasma\candidates\new-candidate\gitedvard-chiasma-123\chiasma'
        self.app_paths.common_move_candidates(project_root)
        expected_file = r'c:\xxx\chiasma\candidates\new-candidate\validation\chiasma.exe'
        self.assertTrue(self.os_module.path.exists(expected_file))

    def test_move_candidates__with_one_file_added_in_bin_release__file_found_in_production(self):
        project_root = r'c:\xxx\chiasma\candidates\new-candidate\gitedvard-chiasma-123\chiasma'
        self.app_paths.common_move_candidates(project_root)
        expected_file = r'c:\xxx\chiasma\candidates\new-candidate\production\chiasma.exe'
        self.assertTrue(self.os_module.path.exists(expected_file))


class FakeBranchProvider:
    def __init__(self):
        self.candidate_version = "1.0.0"
        self.latest_version = "latest-version"
        self.candidate_branch = "new-candidate"
