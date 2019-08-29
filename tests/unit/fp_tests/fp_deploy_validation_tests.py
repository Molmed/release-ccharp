import os
from unittest import skip
from mock import MagicMock
from tests.unit.fp_tests.base import FPBaseTests


class FPValidationDeployTests(FPBaseTests):
    def setUp(self):
        self.setup_fp()
        self.file_builder = FileSystemBuilder(self.fp, self.filesystem)

    def _make_mock(self):
        self.fp.validation_deployer.file_deployer.move_latest_to_archive = MagicMock()
        self.fp.validation_deployer.file_deployer.back_move_from_archive = MagicMock()
        self.fp.validation_deployer.file_deployer.copy_to_latest = MagicMock()
        self.fp.validation_deployer.copy_config_file = MagicMock()

    def test_run__with_no_candidate_in_latest_and_no_archive_dir_for_current_version__only_copy_to_latest_is_called(self):
        # Arrange
        self._make_mock()

        # Act
        self.fp.validation_deployer.run()

        # Assert
        self.fp.validation_deployer.file_deployer.copy_to_latest.assert_called_once_with()
        self.fp.validation_deployer.file_deployer.move_latest_to_archive.assert_not_called()
        self.fp.validation_deployer.file_deployer.back_move_from_archive.assert_not_called()

    def test_run__with_another_candidate_in_latest_and_no_archive_dir_for_current__copy_to_latest_and_move_latest_called(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self._make_mock()

        # Act
        self.fp.validation_deployer.run()

        # Assert
        self.fp.validation_deployer.file_deployer.copy_to_latest.assert_called_once_with()
        self.fp.validation_deployer.file_deployer.move_latest_to_archive.assert_called_once_with('0.1.0')
        self.fp.validation_deployer.file_deployer.back_move_from_archive.assert_not_called()

    def test_run__with_same_candidate_in_latest_and_existent_archive_dir__copy_to_latest_and_back_move_called(self):
        # Arrange
        self.file_builder.add_validation_file_in_archive('validation_file.txt')
        self._make_mock()

        # Act
        self.fp.validation_deployer.run()

        # Assert
        self.fp.validation_deployer.file_deployer.copy_to_latest.assert_called_once_with()
        self.fp.validation_deployer.file_deployer.move_latest_to_archive.assert_not_called()
        self.fp.validation_deployer.file_deployer.back_move_from_archive.called_once_with()

    def test_run__with_another_candidate_in_latest_and_existing_archive_dir__all_methods_called(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_archive('validation_file.txt')
        self._make_mock()

        # Act
        self.fp.validation_deployer.run()

        # Assert
        self.fp.validation_deployer.file_deployer.copy_to_latest.assert_called_once_with()
        self.fp.validation_deployer.file_deployer.move_latest_to_archive.assert_called_once_with('0.1.0')
        self.fp.validation_deployer.file_deployer.back_move_from_archive.called_once_with()

    def test_copy_config__with_config_in_validation__config_file_copied(self):
        # Arrange
        self.file_builder.add_file_in_validation('FPDatabaseConfig.txt')

        # Act
        self.fp.validation_deployer.copy_config_file()

        # Assert
        copied_path = r'c:\xxx\fp\uservalidations\latest\FPDatabaseConfig.txt'
        self.assertTrue(self.os_service.exists(copied_path))

    def test_create_shortcut__with_latest_empty__something_is_copied_to_latest(self):
        self.fp.validation_deployer.path_actions.create_shortcut_to_exe()
        self.assertTrue(self.os_module.path.exists(r'c:\xxx\fp\uservalidations\latest\fpdatabase.lnk'))

    def test_create_shortcut__with_shortcut_exists_in_target__copy_without_error(self):
        fake_destination_link = r'c:\xxx\fp\uservalidations\latest\fpdatabase.lnk'
        self.filesystem.create_file(fake_destination_link)

        # Act
        self.fp.validation_deployer.path_actions.create_shortcut_to_exe()

        # Assert
        self.assertTrue(self.os_module.path.exists(r'c:\xxx\fp\uservalidations\latest\fpdatabase.lnk'))

    def test_create_shortcut__with_target_exists_in_candidates__extract_shortcut_target_works(self):
        # Arrange
        fake_target_path = r'c:\xxx\fp\candidates\release-1.0.0\validation\fpdatabase.exe'
        self.filesystem.create_file(fake_target_path)
        dest_shortcut_path = r'c:\xxx\fp\uservalidations\latest\fpdatabase.lnk'

        # Act
        self.fp.validation_deployer.path_actions.create_shortcut_to_exe()
        shortcut_target = self.fp.validation_deployer.shortcut_examiner.\
            _extract_shortcut_target(dest_shortcut_path)

        #Assert
        self.assertEqual(r'c:\xxx\fp\candidates\release-1.0.0\validation\FPDatabase.exe', shortcut_target)


class FileSystemBuilder:
    def __init__(self, fp, filesystem):
        self.fp = fp
        self.filesystem = filesystem

    def add_shortcut(self, candidate_dir='release-1.0.0'):
        cand_path = os.path.join(self.fp.path_properties.root_candidates, candidate_dir)
        current_shortcut_target = os.path.join(cand_path, r'buildpath\fpdatabase.exe')
        shortcut_save_path = os.path.join(self.fp.path_properties.user_validations_latest, r'fpdatabase.lnk')
        self.fp.windows_commands.create_shortcut(shortcut_save_path, current_shortcut_target)

    def add_validation_file_in_archive(self, filename='validationfile.txt', contents=''):
        """
        Put it in folder matching the candidate version
        :param filename:
        :return:
        """
        path = os.path.join(self.fp.path_properties.archive_dir_validation_files, filename)
        self.filesystem.create_file(path, contents=contents)

    def add_file_in_validation(self, filename='file.txt', contents=''):
        path = os.path.join(self.fp.app_paths.validation_dir, filename)
        self.filesystem.create_file(path, contents=contents)

    def get_contents(self, path):
        c = None
        with self.fp.os_service.open(path, 'r') as f:
            c = f.read()
        return c
