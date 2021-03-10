import os
from unittest import skip
import pytest
from mock import MagicMock
from release_ccharp.apps.common.directory_handling import FileDoesNotExistsException
from tests.unit.order_tests.base import OrderBaseTests
from release_ccharp.utils import create_dirs


class OrderDeployTests(OrderBaseTests):
    def setUp(self):
        self.setup_order()
        self.file_builder = FileSystemBuilder(self.order, self.filesystem)

    def add_required_files(self):
        self.file_builder.add_file_in_production('order.exe')
        self.file_builder.add_file_in_production('order.exe.config')
        self.file_builder.add_file_in_production_config_lab('order.exe.config')

    @pytest.mark.now
    def test_copy_backup__with_backup_added_to_fake_server__backup_exists_in_candidate(self):
        # Arrange
        backup_dir = self.order.deployer.path_properties.db_backup_server_dir
        create_dirs(self.os_service, backup_dir)
        backup_path = os.path.join(backup_dir, self.order.deployer.path_properties.db_backup_filename)
        self.filesystem.create_file(backup_path)

        # Act
        self.order.deployer.copy_backup()

        # Assert
        path = r'c:\xxx\order\candidates\release-1.0.0\order_devel_backup.bak'
        self.assertTrue(self.os_service.exists(path))

    def test_copy_backup__with_path_does_not_exists__exception(self):
        # Arrange
        # do not add backup file...

        # Act
        # Assert
        with self.assertRaises(IOError):
            self.order.deployer.copy_backup()

    def get_magicmock(self):
        m = MagicMock()
        m.__name__ = 'mock'
        return m

    def mock_out_run(self):
        self.order.deployer.check_source_files_exists = self.get_magicmock()
        self.order.deployer.copy_backup = self.get_magicmock()
        self.order.deployer.file_deployer.move_deploy_files = MagicMock()
        self.order.deployer.file_deployer.move_user_manual = MagicMock()
        self.order.deployer.move_to_archive = self.get_magicmock()

    def test_run__with_skip_copy_backup_false__copy_backup_called(self):
        # Arrange
        self.mock_out_run()
        # Act
        self.order.deployer.run()
        # Assert
        self.order.deployer.copy_backup.assert_called_once_with()

    def test_run__with_skip_copy_backup_true__copy_backup_not_called(self):
        # Arrange
        self.mock_out_run()
        # Act
        self.order.deployer.run(skip_copy_backup=True)
        # Assert
        self.order.deployer.copy_backup.assert_not_called()

    def test_check_source_files__with_exe_lacking__throws(self):
        # Arrange
        #self.file_builder.add_file_in_production('order.exe')
        self.file_builder.add_file_in_production('order.exe.config')
        self.file_builder.add_file_in_production_config_lab('order.exe.config')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.order.deployer.run()

    def test_check_source_files__with_config_lacking__throws(self):
        # Arrange
        self.file_builder.add_file_in_production('order.exe')
        #self.file_builder.add_file_in_production('order.exe.config')
        self.file_builder.add_file_in_production_config_lab('order.exe.config')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.order.deployer.run()

    def test_check_source_file__with_config_lab_lacking__throws(self):
        # Arrange
        self.file_builder.add_file_in_production('order.exe')
        self.file_builder.add_file_in_production('order.exe.config')
        # self.file_builder.add_file_in_production_config_lab('order.exe.config')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.order.deployer.run()

    def test_move_files__with_three_files_in_production__files_exists_in_deploy_catalog(self):
        # Arrange
        self.add_required_files()
        # Act
        self.order.deployer.file_deployer.move_deploy_files()
        # Assert
        exe_path = r'c:\xxx\deploy\order.exe'
        standard_config = r'c:\xxx\deploy\order.exe.config'
        lab_config = r'c:\xxx\deploy\Config_lab\order.exe.config'
        self.assertTrue(self.os_module.path.exists(exe_path))
        self.assertTrue(self.os_module.path.exists(standard_config))
        self.assertTrue(self.os_module.path.exists(lab_config))

    def test_move_release_history__release_history_exists__release_history_moved(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_file_in_latest_candidate_dir(r'release-history.txt')
        # Act
        self.order.deployer.file_deployer.copy_release_history()
        # Assert
        release_history = r'c:\xxx\order\doc\release-history.txt'
        self.assertTrue(self.os_module.path.exists(release_history))

    def test_archive_version__with_validation_files_and_sql_script__validation_file_in_archive_folder(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        # Act
        self.order.deployer.move_to_archive()
        # Assert
        archived_validation_file = \
            r'c:\xxx\order\uservalidations\allversions\1.0.0\validationfiles\validationfile.txt'
        self.assertTrue(self.os_module.path.exists(archived_validation_file))

    def test_archive_version__with_validation_files_and_sql_script__validation_files_removed_from_latest(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        # Act
        self.order.deployer.move_to_archive()
        # Assert
        validation_dir_in_latest = \
            r'c:\xxx\order\uservalidations\latest\validationfiles'
        self.assertFalse(self.os_module.path.exists(validation_dir_in_latest))

    def test_archive_version__with_validation_files_and_sql_script__validation_file_removed_from_next(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_validation_file_in_next(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        # Act
        self.order.deployer.move_to_archive()
        # Assert
        path_to_validation_in_next = \
            r'c:\xxx\order\uservalidations\allversions\_next_release\validationfiles\validationfile.txt'
        self.assertFalse(self.os_module.path.exists(path_to_validation_in_next))

    def test_archive_version__with_validation_files_and_sql_script__shortcut_in_archive_folder(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.order.deployer.move_to_archive()
        # Assert
        archived_shortcut = \
            r'c:\xxx\order\uservalidations\allversions\1.0.0\order.lnk'
        self.assertTrue(self.os_module.path.exists(archived_shortcut))

    def test_archive_version__with_validation_files_and_sql_script__shortcut_remains_in_latest(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.order.deployer.move_to_archive()
        # Assert
        shortcut_in_latest = \
            r'c:\xxx\order\uservalidations\latest\order.lnk'
        self.assertTrue(self.os_module.path.exists(shortcut_in_latest))

    def test_archive_version__with_validation_files_and_sql_script__shortcut_target_correct_in_latest(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.order.deployer.move_to_archive()
        # Assert
        shortcut_in_latest = \
            r'c:\xxx\order\uservalidations\latest\order.lnk'
        shortcut_target = self.order.validation_deployer.shortcut_examiner.\
            _extract_shortcut_target(shortcut_in_latest)
        self.assertEqual(r'c:\xxx\order\candidates\release-1.0.0\validation\Order.exe', shortcut_target)

    def test_archive_version__with_validation_files_and_sql_script__sql_script_in_archive_folder(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.order.deployer.move_to_archive()
        # Assert
        archived_script = \
            r'c:\xxx\order\uservalidations\allversions\1.0.0\sqlupdates\script1.sql'
        self.assertTrue(self.os_module.path.exists(archived_script))

    def test_archive_version__with_validation_files_and_sql_script__sql_script_removed_from_next(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.order.deployer.move_to_archive()
        # Assert
        script_path_in_next = \
            r'c:\xxx\order\uservalidations\allversions\_next_release\sqlupdates\script1.sql'
        self.assertFalse(self.os_module.path.exists(script_path_in_next))


class FileSystemBuilder:
    def __init__(self, order, filesystem):
        self.order = order
        self.filesystem = filesystem

    def add_file_in_production(self, filename='filename.txt'):
        path = os.path.join(self.order.app_paths.production_dir, filename)
        self.filesystem.create_file(path)

    def add_file_in_production_config_lab(self, filename='file.txt'):
        path = os.path.join(self.order.app_paths.production_config_lab_dir, filename)
        self.filesystem.create_file(path)

    def add_file_in_current_candidate_dir(self, filename='file.txt'):
        path = os.path.join(self.order.path_properties.current_candidate_dir, filename)
        self.filesystem.create_file(path)

    def add_file_in_latest_candidate_dir(self, filename='file.txt'):
        path = os.path.join(self.order.path_properties.latest_accepted_candidate_dir, filename)
        print('add file into: {}'.format(path))
        self.filesystem.create_file(path)

    def add_validation_file_in_latest(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.order.path_properties.latest_validation_files, filename)
        self.filesystem.create_file(path, contents=contents)

    def add_validation_file_in_next(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.order.path_properties.next_validation_files, filename)
        print('add file into: {}'.format(path))
        self.filesystem.create_file(path, contents=contents)

    def add_sql_script_in_next(self, filename='script1.sql', contents=''):
        path = os.path.join(self.order.path_properties.next_sql_updates, filename)
        print('add file into: {}'.format(path))
        self.filesystem.create_file(path, contents=contents)

    def add_shortcut(self, candidate_dir='release-1.0.0'):
        cand_path = os.path.join(self.order.path_properties.root_candidates, candidate_dir)
        current_shortcut_target = os.path.join(cand_path, r'buildpath\order.exe')
        shortcut_save_path = os.path.join(self.order.path_properties.user_validations_latest, r'order.lnk')
        self.order.windows_commands.create_shortcut(shortcut_save_path, current_shortcut_target)
