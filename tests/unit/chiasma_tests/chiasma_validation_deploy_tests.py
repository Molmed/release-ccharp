import os
from unittest import skip
from tests.unit.chiasma_tests.base import ChiasmaBaseTests


class ChiasmaValidationDeployTests(ChiasmaBaseTests):
    def setUp(self):
        self.setup_chiasma()
        self.file_builder = FileSystemBuilder(self.chiasma, self.filesystem)

    def test_create_shortcut__with_latest_empty__something_is_copied_to_latest(self):
        self.chiasma.validation_deployer.path_actions.create_shortcut_to_exe()
        self.assertTrue(self.os_module.path.exists(r'c:\xxx\chiasma\uservalidations\latest\chiasma.lnk'))

    def test_create_shortcut__with_shortcut_exists_in_target__copy_without_error(self):
        fake_destination_link = r'c:\xxx\chiasma\uservalidations\latest\chiasma.lnk'
        self.filesystem.create_file(fake_destination_link)

        # Act
        self.chiasma.validation_deployer.path_actions.create_shortcut_to_exe()

        # Assert
        self.assertTrue(self.os_module.path.exists(r'c:\xxx\chiasma\uservalidations\latest\chiasma.lnk'))

    def test_create_shortcut__with_target_exists_in_candidates__extract_shortcut_target_works(self):
        # Arrange
        fake_target_path = r'c:\xxx\chiasma\candidates\release-1.0.0\validation\chiasma.exe'
        self.filesystem.create_file(fake_target_path)
        dest_shortcut_path = r'c:\xxx\chiasma\uservalidations\latest\chiasma.lnk'

        # Act
        self.chiasma.validation_deployer.run()
        shortcut_target = self.chiasma.validation_deployer.shortcut_examiner.\
            _extract_shortcut_target(dest_shortcut_path)

        #Assert
        self.assertEqual(r'c:\xxx\chiasma\candidates\release-1.0.0\validation\Chiasma.exe', shortcut_target)

    def test_copy_from_next__with_latest_dir_empty__copied_files_exists_in_latest(self):
        # Arrange
        validation_file = \
            r'c:\xxx\chiasma\uservalidations\allversions\_next_release\validationfiles\validation_file.txt'
        self.filesystem.create_file(validation_file)
        self.file_builder.add_shortcut()

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\chiasma\uservalidations\latest\validationfiles\validation_file.txt'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_hotfix_candidate__files_copied_from_next_hotfix(self):
        # Arrange
        validation_file = \
            r'c:\xxx\chiasma\uservalidations\allversions\_next_hotfix\validationfiles\validation_file.txt'
        self.filesystem.create_file(validation_file)
        self.chiasma.branch_provider.candidate_branch = "hotfix-1.0.1"
        self.file_builder.add_shortcut()

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\chiasma\uservalidations\latest\validationfiles\validation_file.txt'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_branch_and_shortcut_different__validation_files_copied_latest_to_archive(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_latest('old_validation_file.txt')
        self.file_builder.add_validation_file_in_next('new_validation_file.txt')

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\chiasma\uservalidations\allversions\0.1.0\validationfiles\old_validation_file.txt'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_branch_and_shortcut_different__shortcut_copied_to_archive(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_latest('old_validation_file.txt')
        self.file_builder.add_validation_file_in_next('new_validation_file.txt')

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\chiasma\uservalidations\allversions\0.1.0\chiasma.lnk'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_branch_and_shortcut_different__sql_script_not_copied_to_archive(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_latest('old_validation_file.txt')
        self.file_builder.add_validation_file_in_next('new_validation_file.txt')
        self.file_builder.add_sql_script_in_next('script1.sql')

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\chiasma\uservalidations\allversions\0.1.0\sqlupdates\script1.sql'
        self.assertFalse(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_branch_and_shortcut_different__file_deleted_in_latest(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_latest('old_validation_file.txt')
        self.file_builder.add_validation_file_in_next('new_validation_file.txt')

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        old_file = r'c:\xxx\chiasma\uservalidations\latest\validationfiles\old_validation_file.txt'
        self.assertFalse(self.os_module.path.exists(old_file))

    def test_copy_from_next__with_branch_and_shortcut_same__validation_files_not_copied_to_archive(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        self.file_builder.add_validation_file_in_latest('old_validation_file.txt')
        self.file_builder.add_validation_file_in_next('new_validation_file.txt')

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\chiasma\uservalidations\allversions\1.0.0\validationfiles\old_validation_file.txt'
        self.assertFalse(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_file_in_archive__file_exists_in_latest(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_archive('validation_file.txt')

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\chiasma\uservalidations\latest\validationfiles\validation_file.txt'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_file_in_archive__file_removed_in_archive(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_archive('validation_file.txt')

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        source_file = r'c:\xxx\chiasma\uservalidations\allversions\1.0.0\validationfiles\validation_file.txt'
        self.assertFalse(self.os_module.path.exists(source_file))

    def test_copy_from_next__with_file_in_archive__file_from_next_in_latest(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_archive('validation_file.txt')
        self.file_builder.add_validation_file_in_next('file_from_next.txt')

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\chiasma\uservalidations\latest\validationfiles\file_from_next.txt'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__with_same_file_in_next_and_archive__archive_file_in_latest(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-0.1.0')
        self.file_builder.add_validation_file_in_archive('validation_file.txt', contents='archive')
        self.file_builder.add_validation_file_in_next('validation_file.txt', contents='next')

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\chiasma\uservalidations\latest\validationfiles\validation_file.txt'
        self.assertEqual('archive', self.file_builder.get_contents(copied_file))

    def test_copy_from_next__shortcut_nonexistent_in_latest__plain_copy(self):
        # Arrange
        self.file_builder.add_validation_file_in_next('validation_file.txt')

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        copied_file = r'c:\xxx\chiasma\uservalidations\latest\validationfiles\validation_file.txt'
        self.assertTrue(self.os_module.path.exists(copied_file))

    def test_copy_from_next__ordinary_setup__only_one_catalog_and_shortcut_in_latest(self):
        # Arrange
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        self.file_builder.add_validation_file_in_next('validation_file.txt')

        # Act
        self.chiasma.validation_deployer.copy_validation_files()

        # Assert
        latest = r'c:\xxx\chiasma\uservalidations\latest'
        dir_objects = [o for o in self.chiasma.os_service.listdir(latest)]
        self.assertEqual(2, len(dir_objects))


class FileSystemBuilder:
    def __init__(self, chiasma, filesystem):
        self.chiasma = chiasma
        self.filesystem = filesystem

    def add_shortcut(self, candidate_dir='release-1.0.0'):
        cand_path = os.path.join(self.chiasma.path_properties.root_candidates, candidate_dir)
        current_shortcut_target = os.path.join(cand_path, r'buildpath\chiasma.exe')
        shortcut_save_path = os.path.join(self.chiasma.path_properties.user_validations_latest, r'chiasma.lnk')
        self.chiasma.windows_commands.create_shortcut(shortcut_save_path, current_shortcut_target)

    def add_validation_file_in_latest(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.chiasma.path_properties.latest_validation_files, filename)
        self.filesystem.create_file(path, contents=contents)

    def add_validation_file_in_next(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.chiasma.path_properties.next_validation_files, filename)
        self.filesystem.create_file(path, contents=contents)

    def add_sql_script_in_next(self, filename='script1.sql', contents=''):
        path = os.path.join(self.chiasma.path_properties.next_sql_updates, filename)
        self.filesystem.create_file(path, contents=contents)

    def add_validation_file_in_archive(self, filename='validationfile.txt', contents=''):
        """
        Put it in folder matching the candidate version
        :param filename:
        :return:
        """
        path = os.path.join(self.chiasma.path_properties.archive_dir_validation_files, filename)
        self.filesystem.create_file(path, contents=contents)

    def get_contents(self, path):
        c = None
        with self.chiasma.os_service.open(path, 'r') as f:
            c = f.read()
        return c
