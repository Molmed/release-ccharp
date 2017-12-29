import unittest
import os
from unittest import skip
from pyfakefs import fake_filesystem
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.apps.chiasma import Application
from release_ccharp.apps.chiasma_scripts.deployer import FileDoesNotExistsException
from tests.unit.utility.fake_os_service import FakeOsService
from tests.unit.utility.fake_windows_commands import FakeWindowsCommands


class ChiasmaDeployTests(unittest.TestCase):
    def setUp(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "chiasma",
            "owner": "GitEdvard"
        }
        branch_provider = FakeBranchProvider()
        wf = SnpseqWorkflow(whatif=False, repo="chiasma")
        wf.config = config
        wf.paths.config = config
        wf.paths.branch_provider = branch_provider
        self.filesystem = fake_filesystem.FakeFilesystem()
        os_service = FakeOsService(self.filesystem)
        self.os_module = os_service.os_module
        self.chiasma = Application(wf, branch_provider, os_service,
                                   FakeWindowsCommands(self.filesystem), whatif=False)
        self.file_builder = FileSystemBuilder(self.chiasma, self.filesystem)

        path_actions = SnpseqPathActions(
            whatif=False, snpseq_path_properties=self.chiasma.path_properties,
            os_service=os_service
        )
        path_actions.generate_folder_tree()

    def test_check_source_files__with_exe_lacking__throws(self):
        # Arrange
        #self.file_builder.add_file_in_production('chiasma.exe')
        self.file_builder.add_file_in_production('chiasma.exe.config')
        self.file_builder.add_file_in_production_config_lab('chiasma.exe.config')
        self.file_builder.add_file_in_current_candidate_dir('chiasma-user-manual-v1.0.0.pdf')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.chiasma.deployer.run()

    def test_check_source_files__with_config_lacking__throws(self):
        # Arrange
        self.file_builder.add_file_in_production('chiasma.exe')
        #self.file_builder.add_file_in_production('chiasma.exe.config')
        self.file_builder.add_file_in_production_config_lab('chiasma.exe.config')
        self.file_builder.add_file_in_current_candidate_dir('chiasma-user-manual-v1.0.0.pdf')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.chiasma.deployer.run()

    def test_check_source_file__with_config_lab_lacking__throws(self):
        # Arrange
        self.file_builder.add_file_in_production('chiasma.exe')
        self.file_builder.add_file_in_production('chiasma.exe.config')
        # self.file_builder.add_file_in_production_config_lab('chiasma.exe.config')
        self.file_builder.add_file_in_current_candidate_dir('chiasma-user-manual-v1.0.0.pdf')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.chiasma.deployer.run()

    def test_check_source_file__with_user_manual_lacking__throws(self):
        # Arrange
        self.file_builder.add_file_in_production('chiasma.exe')
        self.file_builder.add_file_in_production('chiasma.exe.config')
        self.file_builder.add_file_in_production_config_lab('chiasma.exe.config')
        #self.file_builder.add_file_in_current_candidate_dir('chiasma-user-manual-v1.0.0.pdf')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.chiasma.deployer.run()


class FakeBranchProvider:
    def __init__(self):
        self.candidate_version = "1.0.0"
        self.latest_version = "latest-version"
        self.candidate_branch = "release-1.0.0"


class FileSystemBuilder:
    def __init__(self, chiasma, filesystem):
        self.chiasma = chiasma
        self.filesystem = filesystem

    def add_file_in_production(self, filename='filename.txt'):
        path = os.path.join(self.chiasma.app_paths.production_dir, filename)
        self.filesystem.CreateFile(path)

    def add_file_in_production_config_lab(self, filename='file.txt'):
        path = os.path.join(self.chiasma.app_paths.production_config_lab_dir, filename)
        self.filesystem.CreateFile(path)

    def add_file_in_current_candidate_dir(self, filename='file.txt'):
        path = os.path.join(self.chiasma.path_properties.current_candidate_dir, filename)
