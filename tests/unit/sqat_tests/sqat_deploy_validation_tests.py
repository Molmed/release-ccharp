from __future__ import print_function
import os
from tests.unit.sqat_tests.base import SqatBaseTests


class SqatDeployValidationTests(SqatBaseTests):
    def setUp(self):
        self.setup_sqat()
        self.file_builder = FileSystemBuilder(self.sqat, self.filesystem)

    def test_create_shortcut__with_target_exists_in_candidates__extract_shortcut_target_works(self):
        # Arrange
        fake_target_path = r'c:\xxx\sqat\candidates\release-1.0.0\validation\sqat.exe'
        self.filesystem.create_file(fake_target_path)
        dest_shortcut_path = r'c:\xxx\sqat\uservalidations\latest\sqat.lnk'

        # Act
        self.sqat.validation_deployer.path_actions.create_shortcut_to_exe()
        shortcut_target = self.sqat.validation_deployer.shortcut_examiner.\
            _extract_shortcut_target(dest_shortcut_path)

        #Assert
        self.assertEqual(r'c:\xxx\sqat\candidates\release-1.0.0\validation\sqat.exe', shortcut_target)

    def test_copy_from_next__with_latest_dir_empty__copied_files_exists_in_latest(self):
        # Arrange
        validation_file = \
            r'c:\xxx\sqat\uservalidations\allversions\_next_release\validationfiles\validation_file.txt'
        self.filesystem.create_file(validation_file)
        self.file_builder.add_shortcut()

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\sqat\uservalidations\latest\validationfiles\validation_file.txt'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_branch_and_shortcut_different__validation_files_copied_latest_to_archive(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_latest('old_validation_file.txt')
        self.file_builder.add_validation_file_in_next('new_validation_file.txt')

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\sqat\uservalidations\allversions\0.1.0\validationfiles\old_validation_file.txt'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_branch_and_shortcut_different__shortcut_copied_to_archive(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_latest('old_validation_file.txt')
        self.file_builder.add_validation_file_in_next('new_validation_file.txt')

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\sqat\uservalidations\allversions\0.1.0\sqat.lnk'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_branch_and_shortcut_different__sql_script_not_copied_to_archive(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_latest('old_validation_file.txt')
        self.file_builder.add_validation_file_in_next('new_validation_file.txt')
        self.file_builder.add_sql_script_in_next('script1.sql')

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\sqat\uservalidations\allversions\0.1.0\sqlupdates\script1.sql'
        self.assertFalse(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_branch_and_shortcut_different__file_deleted_in_latest(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_latest('old_validation_file.txt')
        self.file_builder.add_validation_file_in_next('new_validation_file.txt')

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        old_file = r'c:\xxx\sqat\uservalidations\latest\validationfiles\old_validation_file.txt'
        self.assertFalse(self.os_module.path.exists(old_file))

    def test_copy_from_next__with_branch_and_shortcut_same__validation_files_not_copied_to_archive(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        self.file_builder.add_validation_file_in_latest('old_validation_file.txt')
        self.file_builder.add_validation_file_in_next('new_validation_file.txt')

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\sqat\uservalidations\allversions\1.0.0\validationfiles\old_validation_file.txt'
        self.assertFalse(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_file_in_archive__file_exists_in_latest(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_archive('validation_file.txt')

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\sqat\uservalidations\latest\validationfiles\validation_file.txt'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_file_in_archive__file_removed_in_archive(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_archive('validation_file.txt')

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        source_file = r'c:\xxx\sqat\uservalidations\allversions\1.0.0\validationfiles\validation_file.txt'
        self.assertFalse(self.os_module.path.exists(source_file))

    def test_copy_from_next__with_file_in_archive__file_from_next_in_latest(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_archive('validation_file.txt')
        self.file_builder.add_validation_file_in_next('file_from_next.txt')

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\sqat\uservalidations\latest\validationfiles\file_from_next.txt'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_same_file_in_next_and_archive__archive_file_in_latest(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_archive('validation_file.txt', contents='archive')
        self.file_builder.add_validation_file_in_next('validation_file.txt', contents='next')

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\sqat\uservalidations\latest\validationfiles\validation_file.txt'
        self.assertEqual('archive', self.file_builder.get_contents(copied_file))

    def test_copy_from_next__shortcut_nonexistent_in_latest__plain_copy(self):
        # Arrange
        self.file_builder.add_validation_file_in_next('validation_file.txt')

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\sqat\uservalidations\latest\validationfiles\validation_file.txt'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__ordinary_setup__only_one_catalog_and_shortcut_in_latest(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        self.file_builder.add_validation_file_in_next('validation_file.txt')

        # Act
        self.sqat.validation_deployer.copy_validation_files()

        # Assert
        latest = r'c:\xxx\sqat\uservalidations\latest'
        dir_objects = [o for o in self.sqat.os_service.listdir(latest)]
        self.assertEqual(2, len(dir_objects))


class FileSystemBuilder:
    def __init__(self, sqat, filesystem):
        self.sqat = sqat
        self.filesystem = filesystem

    def add_shortcut(self, candidate_dir='release-1.0.0'):
        cand_path = os.path.join(self.sqat.path_properties.root_candidates, candidate_dir)
        current_shortcut_target = os.path.join(cand_path, r'buildpath\sqat.exe')
        shortcut_save_path = os.path.join(self.sqat.path_properties.user_validations_latest, r'sqat.lnk')
        self.sqat.windows_commands.create_shortcut(shortcut_save_path, current_shortcut_target)

    def add_validation_file_in_latest(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.sqat.path_properties.latest_validation_files, filename)
        self.filesystem.create_file(path, contents=contents)

    def add_validation_file_in_next(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.sqat.path_properties.next_validation_files, filename)
        self.filesystem.create_file(path, contents=contents)

    def add_sql_script_in_next(self, filename='script1.sql', contents=''):
        path = os.path.join(self.sqat.path_properties.next_sql_updates, filename)
        self.filesystem.create_file(path, contents=contents)

    def add_validation_file_in_archive(self, filename='validationfile.txt', contents=''):
        """
        Put it in folder matching the candidate version
        :param filename:
        :return:
        """
        path = os.path.join(self.sqat.path_properties.archive_dir_validation_files, filename)
        self.filesystem.create_file(path, contents=contents)

    def get_contents(self, path):
        c = None
        with self.sqat.os_service.open(path, 'r') as f:
            c = f.read()
        return c

    def _log(self, path):
        print('add file into: {}'.format(path))
