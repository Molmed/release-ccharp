import os
from unittest import skip
from mock import MagicMock
from release_ccharp.apps.common.directory_handling import FileDoesNotExistsException
from tests.unit.fp_tests.base import FPBaseTests


class ChiasmaDeployTests(FPBaseTests):
    def setUp(self):
        self.setup_fp()
        self.file_builder = FileSystemBuilder(self.fp, self.filesystem)

    def add_required_files(self):
        self.file_builder.add_file_in_production('fpdatabase.exe')
        self.file_builder.add_file_in_production('fpdatabase.exe.config')
        self.file_builder.add_file_in_production('fpdatabaseconfig.txt')

    def _make_mocks(self):
        self.fp.deployer.check_source_files_exists = MagicMock()
        self.fp.deployer.file_deployer.move_deploy_files = MagicMock()
        self.fp.deployer.move_to_archive = MagicMock()

    def test_run__with_mocked_methods__move_deploy_files_called(self):
        # Arrange
        self._make_mocks()

        # Act
        self.fp.deployer.run()

        # Assert
        self.fp.deployer.file_deployer.move_deploy_files.assert_called_once_with()

    def test_run__with_mocked_methods__move_to_archive_called(self):
        # Arrange
        self._make_mocks()

        # Act
        self.fp.deployer.run()

        # Assert
        self.fp.deployer.move_to_archive.assert_called_once_with()

    def test_check_source_files__with_exe_lacking__throws(self):
        # Arrange
        #self.file_builder.add_file_in_production('fpdatabase.exe')
        self.file_builder.add_file_in_production('fpdatabase.exe.config')
        self.file_builder.add_file_in_production('fpdatabaseconfig.txt')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.fp.deployer.run()

    def test_check_source_files__with_xml_config_lacking__throws(self):
        # Arrange
        self.file_builder.add_file_in_production('fpdatabase.exe')
        #self.file_builder.add_file_in_production('fpdatabase.exe.config')
        self.file_builder.add_file_in_production('fpdatabaseconfig.txt')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.fp.deployer.run()

    def test_check_source_file__with_txt_config_lacking__throws(self):
        # Arrange
        self.file_builder.add_file_in_production('fpdatabase.exe')
        self.file_builder.add_file_in_production('fpdatabase.exe.config')
        # self.file_builder.add_file_in_production('fpdatabaseconfig.txt')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.fp.deployer.run()


class FileSystemBuilder:
    def __init__(self, fp, filesystem):
        self.fp = fp
        self.filesystem = filesystem

    def add_file_in_production(self, filename='filename.txt'):
        path = os.path.join(self.fp.app_paths.production_dir, filename)
        self.filesystem.CreateFile(path)

    def add_file_in_production_config_lab(self, filename='file.txt'):
        path = os.path.join(self.fp.app_paths.production_config_lab_dir, filename)
        self.filesystem.CreateFile(path)

    def add_file_in_current_candidate_dir(self, filename='file.txt'):
        path = os.path.join(self.fp.path_properties.current_candidate_dir, filename)
        self.filesystem.CreateFile(path)

    def add_file_in_latest_candidate_dir(self, filename='file.txt'):
        path = os.path.join(self.fp.path_properties.latest_accepted_candidate_dir, filename)
        print('add file into: {}'.format(path))
        self.filesystem.CreateFile(path)

    def add_validation_file_in_latest(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.fp.path_properties.latest_validation_files, filename)
        self.filesystem.CreateFile(path, contents=contents)

    def add_validation_file_in_next(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.fp.path_properties.next_validation_files, filename)
        print('add file into: {}'.format(path))
        self.filesystem.CreateFile(path, contents=contents)

    def add_sql_script_in_next(self, filename='script1.sql', contents=''):
        path = os.path.join(self.fp.path_properties.next_sql_updates, filename)
        print('add file into: {}'.format(path))
        self.filesystem.CreateFile(path, contents=contents)

    def add_shortcut(self, candidate_dir='release-1.0.0'):
        cand_path = os.path.join(self.fp.path_properties.root_candidates, candidate_dir)
        current_shortcut_target = os.path.join(cand_path, r'buildpath\fpdatabase.exe')
        shortcut_save_path = os.path.join(self.fp.path_properties.user_validations_latest, r'fpdatabase.lnk')
        self.fp.windows_commands.create_shortcut(shortcut_save_path, current_shortcut_target)