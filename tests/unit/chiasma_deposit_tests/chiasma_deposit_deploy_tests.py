import os
from unittest import skip
from mock import MagicMock
from release_ccharp.apps.common.directory_handling import FileDoesNotExistsException
from tests.unit.chiasma_deposit_tests.base import ChiasmaDepositBaseTests
from release_ccharp.utils import create_dirs


class ChiasmaDepositDeployTests(ChiasmaDepositBaseTests):
    def setUp(self):
        self.setup_chiasma_deposit()
        self.file_builder = FileSystemBuilder(self.chiasma_deposit, self.filesystem)

    def add_required_files(self):
        self.file_builder.add_file_in_production('chiasmadeposit.exe')
        self.file_builder.add_file_in_production('chiasmadeposit.exe.config')

    def test_check_source_files__with_exe_lacking__throws(self):
        # Arrange
        #self.file_builder.add_file_in_production('chiasmadeposit.exe')
        self.file_builder.add_file_in_production('chiasmadeposit.exe.config')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.chiasma_deposit.deployer.run()

    def test_check_source_files__with_config_lacking__throws(self):
        # Arrange
        self.file_builder.add_file_in_production('chiasmadeposit.exe')
        #self.file_builder.add_file_in_production('chiasmadeposit.exe.config')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.chiasma_deposit.deployer.run()

    def test_check_source_files__with_nothing_lacking__no_exception(self):
        # Arrange
        self.file_builder.add_file_in_production('chiasmadeposit.exe')
        self.file_builder.add_file_in_production('chiasmadeposit.exe.config')
        # Act
        # Assert
        self.chiasma_deposit.deployer.run()

    def test_move_files__with_two_files_in_production__files_exists_in_deploy_catalog(self):
        # Arrange
        self.add_required_files()
        # Act
        self.chiasma_deposit.deployer.file_deployer.move_deploy_files()
        # Assert
        exe_path = r'c:\xxx\deploy\chiasmadeposit.exe'
        standard_config = r'c:\xxx\deploy\chiasmadeposit.exe.config'
        self.assertTrue(self.os_module.path.exists(exe_path))
        self.assertTrue(self.os_module.path.exists(standard_config))

    def test_move_release_history__release_history_exists__release_history_moved(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_file_in_latest_candidate_dir(r'release-history.txt')
        # Act
        self.chiasma_deposit.deployer.file_deployer.copy_release_history()
        # Assert
        release_history = r'c:\xxx\chiasmadeposit\doc\release-history.txt'
        self.assertTrue(self.os_module.path.exists(release_history))

    def test_archive_version__with_validation_files__validation_file_in_archive_folder(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        # Act
        self.chiasma_deposit.deployer.move_to_archive()
        # Assert
        archived_validation_file = \
            r'c:\xxx\chiasmadeposit\uservalidations\allversions\1.0.0\validationfiles\validationfile.txt'
        self.assertTrue(self.os_module.path.exists(archived_validation_file))

    def test_archive_version__with_validation_files__validation_files_removed_from_latest(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        # Act
        self.chiasma_deposit.deployer.move_to_archive()
        # Assert
        validation_dir_in_latest = \
            r'c:\xxx\chiasmadeposit\uservalidations\latest\validationfiles'
        self.assertFalse(self.os_module.path.exists(validation_dir_in_latest))

    def test_archive_version__with_validation_files__validation_file_removed_from_next(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_validation_file_in_next(r'validationfile.txt')
        # Act
        self.chiasma_deposit.deployer.move_to_archive()
        # Assert
        path_to_validation_in_next = \
            r'c:\xxx\chiasmadeposit\uservalidations\allversions\_next_release\validationfiles\validationfile.txt'
        self.assertFalse(self.os_module.path.exists(path_to_validation_in_next))

    def test_archive_version__with_validation_files__shortcut_in_archive_folder(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.chiasma_deposit.deployer.move_to_archive()
        # Assert
        archived_shortcut = \
            r'c:\xxx\chiasmadeposit\uservalidations\allversions\1.0.0\chiasmadeposit.lnk'
        self.assertTrue(self.os_module.path.exists(archived_shortcut))

    def test_archive_version__with_validation_files__shortcut_remains_in_latest(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.chiasma_deposit.deployer.move_to_archive()
        # Assert
        shortcut_in_latest = \
            r'c:\xxx\chiasmadeposit\uservalidations\latest\chiasmadeposit.lnk'
        self.assertTrue(self.os_module.path.exists(shortcut_in_latest))

    def test_archive_version__with_validation_files__shortcut_target_correct_in_latest(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.chiasma_deposit.deployer.move_to_archive()
        # Assert
        shortcut_in_latest = \
            r'c:\xxx\chiasmadeposit\uservalidations\latest\chiasmadeposit.lnk'
        shortcut_target = self.chiasma_deposit.validation_deployer.shortcut_examiner.\
            _extract_shortcut_target(shortcut_in_latest)
        self.assertEqual(r'c:\xxx\chiasmadeposit\candidates\release-1.0.0\validation\ChiasmaDeposit.exe', shortcut_target)



class FileSystemBuilder:
    def __init__(self, chiasma_deposit, filesystem):
        self.chiasma_deposit = chiasma_deposit
        self.filesystem = filesystem

    def add_file_in_production(self, filename='filename.txt'):
        path = os.path.join(self.chiasma_deposit.app_paths.production_dir, filename)
        self.filesystem.CreateFile(path)

    def add_file_in_latest_candidate_dir(self, filename='file.txt'):
        path = os.path.join(self.chiasma_deposit.path_properties.latest_accepted_candidate_dir, filename)
        print('add file into: {}'.format(path))
        self.filesystem.CreateFile(path)

    def add_validation_file_in_latest(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.chiasma_deposit.path_properties.latest_validation_files, filename)
        self.filesystem.CreateFile(path, contents=contents)

    def add_validation_file_in_next(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.chiasma_deposit.path_properties.next_validation_files, filename)
        print('add file into: {}'.format(path))
        self.filesystem.CreateFile(path, contents=contents)

    def add_shortcut(self, candidate_dir='release-1.0.0'):
        cand_path = os.path.join(self.chiasma_deposit.path_properties.root_candidates, candidate_dir)
        current_shortcut_target = os.path.join(cand_path, r'buildpath\chiasmadeposit.exe')
        shortcut_save_path = os.path.join(self.chiasma_deposit.path_properties.user_validations_latest, r'chiasmadeposit.lnk')
        self.chiasma_deposit.windows_commands.create_shortcut(shortcut_save_path, current_shortcut_target)
