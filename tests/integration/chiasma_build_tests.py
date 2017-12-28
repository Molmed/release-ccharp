from __future__ import print_function
import unittest
from release_ccharp.apps.chiasma import Application
from release_ccharp.apps.common import WindowsCommands
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.utility.os_service import OsService
from release_ccharp.apps.dev_environment import TestEnvironmentProvider


class ChiasmaBuildTests(unittest.TestCase):
    def setUp(self):
        config = {
            "root_path": r'c:\tmp',
            "git_repo_name": "chiasma",
            "confluence_space_key": "CHI",
            "owner": "GitEdvard"
        }
        branch_provider = FakeBranchProvider()
        wf = SnpseqWorkflow(whatif=False, repo="chiasma")
        wf.config = config
        wf.paths.config = config
        wf.paths.branch_provider = branch_provider
        self.chiasma = Application(wf, branch_provider, OsService(),
                                   WindowsCommands(), whatif=False)

    @unittest.skip("Requires folder structure setup")
    def test__check_build_not_already_run__with_validation_folder_already_existing__exception(self):
        self.chiasma.chiasma_builder.check_build_not_already_run()

    @unittest.skip("Writes to harddisk")
    def test__generate_environment(self):
        config = {
            "root_path": r'c:\tmp\test_generate',
            "git_repo_name": "testing-repo",
            "confluence_space_key": "CHI",
            "owner": "GitEdvard"
        }
        provider = TestEnvironmentProvider()
        provider.generate(config)
        self.assertEqual(1,2)

    @unittest.skip("The name contains sha and changes")
    def test_find_download_directory(self):
        name = self.chiasma.app_paths.find_download_directory_name()
        self.assertEqual("", name)

    @unittest.skip("")
    def test__update_binary_version(self):
        self.chiasma.chiasma_builder.update_binary_version()
        self.assertEqual(1,2)

    @unittest.skip("Takes time, and requires code tree downloaded in folder structure")
    def test_build_solution(self):
        self.chiasma.chiasma_builder.build_solution()
        self.assertEqual(1,2)

    @unittest.skip("Fails if validation or production directory already exists")
    def test_move_candidates(self):
        self.chiasma.chiasma_builder.move_candidates()
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_transform_config(self):
        self.chiasma.chiasma_builder.transform_config()
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_build(self):
        self.chiasma.build()
        self.assertEqual(1,2)


class FakeBranchProvider:
    def __init__(self):
        self.candidate_version = "1.0.0"
        self.latest_version = "latest-version"
        self.candidate_branch = "new-candidate"