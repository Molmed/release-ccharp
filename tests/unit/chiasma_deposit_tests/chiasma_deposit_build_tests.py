from __future__ import print_function
import os
from unittest import skip
from pyfakefs.fake_filesystem import FakeFileOpen
from release_ccharp.apps.common.single_file_read_write import StandardVSConfigXML
from release_ccharp.utils import create_dirs
from tests.unit.utility.config import CHIASMA_DEPOSIT_CONFIG
from tests.unit.chiasma_deposit_tests.base import ChiasmaDepositBaseTests


class ChiasmaDepositBuildTests(ChiasmaDepositBaseTests):
    def setUp(self):
        self.setup_chiasma_deposit()
        validation_config_path = (r'c:\xxx\chiasmadeposit\candidates\validation\chiasmadeposit.exe.config')
        self.filesystem.create_file(validation_config_path, contents=CHIASMA_DEPOSIT_CONFIG)
        self.file_builder = FileBuilder(self.filesystem, self.os_service)

    def test__get_version(self):
        version = self.chiasma_deposit.branch_provider.candidate_version
        self.assertEqual("1.0.0", version)

    def test__repo_root(self):
        root_path = self.chiasma_deposit.path_properties._repo_root
        self.assertEqual(r'c:\xxx\chiasmadeposit', root_path)

    def test_replace_assebly_version(self):
        content_list = [
                'line1',
                '[assembly: AssemblyVersion("1.0.*")]',
                'line 3'
        ]
        content = str.join('\n', content_list)
        (current, new) = self.chiasma_deposit.binary_version_updater.get_assembly_replace_strings(content, "1.0.0")
        self.assertEqual("assembly: AssemblyVersion(\"1.0.*\")", current)
        self.assertEqual("assembly: AssemblyVersion(\"1.0.0\")", new)

    def test_move_candidates__with_exe_added_to_release__file_copied_to_production(self):
        # Arrange
        self.file_builder.add_file_to_release('chiasmadeposit.exe')

        # Act
        self.chiasma_deposit.chiasma_deposit_builder.move_candidates()

        # Assert
        production_exe_path = r'c:\xxx\chiasmadeposit\candidates\release-1.0.0\production\chiasmadeposit.exe'
        self.assertTrue(self.os_service.exists(production_exe_path))

    def test_move_candidates__with_exe_added_to_release__file_copied_to_validation(self):
        # Arrange
        self.file_builder.add_file_to_release('chiasmadeposit.exe')

        # Act
        self.chiasma_deposit.chiasma_deposit_builder.move_candidates()

        # Assert
        production_exe_path = r'c:\xxx\chiasmadeposit\candidates\release-1.0.0\validation\chiasmadeposit.exe'
        self.assertTrue(self.os_service.exists(production_exe_path))

    def test_transform_config__with_validation_directory__orig_file_backed_up(self):
        # Arrange
        validation_dir = r'c:\xxx\chiasmadeposit\candidates\validation'

        # Act
        self.chiasma_deposit.chiasma_deposit_builder._transform_config(validation_dir)

        # Assert
        backuped_file = r'c:\xxx\chiasmadeposit\candidates\validation\chiasmadeposit.exe.config.orig'
        self.assertTrue(self.os_module.path.exists(backuped_file))

    def test_transform_config__with_validation_directory__backed_up_config_one_changed_entry_ok(self):
        validation_dir = r'c:\xxx\chiasmadeposit\candidates\validation'
        self.chiasma_deposit.chiasma_deposit_builder._transform_config(validation_dir)
        config_file_path = r'c:\xxx\chiasmadeposit\candidates\validation\chiasmadeposit.exe.config.orig'
        with self.chiasma_deposit.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "ChiasmaDeposit.Properties")
            self.assertEqual("OFFICE", config.get('ApplicationMode'))

    def test_transform_config__with_validation_directory__config_update_ok(self):
        validation_dir = r'c:\xxx\chiasmadeposit\candidates\validation'
        self.chiasma_deposit.chiasma_deposit_builder._transform_config(validation_dir)
        config_file_path = r'c:\xxx\chiasmadeposit\candidates\validation\chiasmadeposit.exe.config'
        with self.chiasma_deposit.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "ChiasmaDeposit.Properties")
            self.assertEqual("GTDB2_practice", config.get('DatabaseName'))
            self.assertEqual("LAB", config.get("ApplicationMode"))
            self.assertEqual("True", config.get("EnforceAppVersion"))

    def test_transform_config__with_release_directory__config_update_ok(self):
        self.file_builder.create_production_config_file()
        release_dir = r'c:\xxx\chiasmadeposit\candidates\release-1.0.0\production'
        self.chiasma_deposit.chiasma_deposit_builder._transform_config(release_dir)
        config_file_path = r'c:\xxx\chiasmadeposit\candidates\release-1.0.0\production\chiasmadeposit.exe.config'
        with self.chiasma_deposit.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "ChiasmaDeposit.Properties")
            self.assertEqual("GTDB2", config.get('DatabaseName'))
            self.assertEqual("LAB", config.get("ApplicationMode"))
            self.assertEqual("True", config.get("EnforceAppVersion"))

    def test_update_binary_version__with_excerp_from_real_file__update_ok(self):
        original_contents_list = ['row 1',
                                  '[assembly: AssemblyVersion("1.0.*")]',
                                  'row 3']
        original_contents = str.join('\n', original_contents_list)
        expected_list = ['row 1',
                         '[assembly: AssemblyVersion("1.0.0")]',
                         'row 3']
        expected = str.join('\n', expected_list)
        file_path = (r'c:\xxx\chiasmadeposit\candidates\release-1.0.0\GitEdvard-chiasmadeposit-123\chiasmadeposit'
                     r'\properties\AssemblyInfo.cs')
        self.filesystem.create_file(file_path, contents=original_contents)
        self.chiasma_deposit.chiasma_deposit_builder.update_binary_version()
        file_module = FakeFileOpen(self.filesystem)
        with file_module(file_path) as f:
            contents = "".join([line for line in f])
        self.assertEqual(expected, contents)

    def test_build_solution__with_solution_file_added_in_chiasmadeposit_dir__no_errors(self):
        # Arrange
        solution_file_path = (r'c:\xxx\chiasmadeposit\candidates\release-1.0.0\gitedvard-chiasmadeposit-123'
                              r'\chiasmadeposit.sln')
        self.filesystem.create_file(solution_file_path)

        # Act
        self.chiasma_deposit.chiasma_deposit_builder.build_solution()


class FileBuilder:
    def __init__(self, filesystem, os_service):
        self.filesystem = filesystem
        self.release_dir = r'c:\xxx\chiasmadeposit\candidates\release-1.0.0\gitedvard-chiasmadeposit-123\chiasmadeposit\bin\release'
        create_dirs(os_service, self.release_dir)

    def create_production_config_file(self):
        release_config_path = (r'c:\xxx\chiasmadeposit\candidates\release-1.0.0\production\chiasmadeposit.exe.config')
        self.filesystem.create_file(release_config_path, contents=CHIASMA_DEPOSIT_CONFIG)

    def add_file_to_release(self, filename='file.txt', contents=''):
        path = os.path.join(self.release_dir, filename)
        self._log(path)
        self.filesystem.create_file(path, contents=contents)

    def _log(self, file_path):
        print('add file into: {}'.format(file_path))
