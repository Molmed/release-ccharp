import os
from unittest import skip
from release_ccharp.apps.common.directory_handling import FileDoesNotExistsException
from tests.unit.sqat_tests.base import SqatBaseTests


class SqatDeployTests(SqatBaseTests):
    def setUp(self):
        self.setup_sqat()
        self.file_builder = FileSystemBuilder(self.sqat, self.filesystem)

    def add_required_files(self):
        self.file_builder.add_file_in_production('sqat.exe')
        self.file_builder.add_file_in_production('sqatconnect.xml')
        self.file_builder.add_file_in_production('sqatconfig.xml')

    def test_check_source_files__with_exe_lacking__throws(self):
        # Arrange
        #self.file_builder.add_file_in_production('sqat.exe')
        self.file_builder.add_file_in_production('sqatconnect.xml')
        self.file_builder.add_file_in_production('sqatconfig.xml')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.sqat.deployer.run()

    def test_check_source_files__with_connect_file_lacking__throws(self):
        # Arrange
        self.file_builder.add_file_in_production('sqat.exe')
        #self.file_builder.add_file_in_production('sqatconnect.xml')
        self.file_builder.add_file_in_production('sqatconfig.xml')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.sqat.deployer.run()

    def test_check_source_files__with_config_file_lacking__throws(self):
        # Arrange
        self.file_builder.add_file_in_production('sqat.exe')
        self.file_builder.add_file_in_production('sqatconnect.xml')
        #self.file_builder.add_file_in_production('sqatconfig.xml')
        # Act
        # Assert
        with self.assertRaises(FileDoesNotExistsException):
            self.sqat.deployer.run()

    def test_move_files__with_three_files_in_production__files_exists_in_deploy_catalog(self):
        # Arrange
        self.add_required_files()
        # Act
        self.sqat.deployer.file_deployer.move_deploy_files()
        # Assert
        exe_path = r'c:\xxx\deploy\sqat.exe'
        config = r'c:\xxx\deploy\sqatconfig.xml'
        connect = r'c:\xxx\deploy\sqatconnect.xml'
        self.assertTrue(self.os_module.path.exists(exe_path))
        self.assertTrue(self.os_module.path.exists(config))
        self.assertTrue(self.os_module.path.exists(connect))

    def test_move_release_history__release_history_exists__release_history_moved(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_file_in_latest_candidate_dir(r'release-history.txt')
        # Act
        self.sqat.deployer.file_deployer.copy_release_history()
        # Assert
        release_history = r'c:\xxx\sqat\doc\release-history.txt'
        self.assertTrue(self.os_module.path.exists(release_history))

    def test_archive_version__with_validation_files_and_sql_script__validation_file_in_archive_folder(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        # Act
        self.sqat.deployer.move_to_archive()
        # Assert
        archived_validation_file = \
            r'c:\xxx\sqat\uservalidations\allversions\1.0.0\validationfiles\validationfile.txt'
        self.assertTrue(self.os_module.path.exists(archived_validation_file))

    def test_archive_version__with_validation_files_and_sql_script__validation_files_removed_from_latest(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        # Act
        self.sqat.deployer.move_to_archive()
        # Assert
        validation_dir_in_latest = \
            r'c:\xxx\sqat\uservalidations\latest\validationfiles'
        self.assertFalse(self.os_module.path.exists(validation_dir_in_latest))

    def test_archive_version__with_validation_files_and_sql_script__validation_file_removed_from_next(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_validation_file_in_next(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        # Act
        self.sqat.deployer.move_to_archive()
        # Assert
        path_to_validation_in_next = \
            r'c:\xxx\sqat\uservalidations\allversions\_next_release\validationfiles\validationfile.txt'
        self.assertFalse(self.os_module.path.exists(path_to_validation_in_next))

    def test_archive_version__with_validation_files_and_sql_script__shortcut_in_archive_folder(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.sqat.deployer.move_to_archive()
        # Assert
        archived_shortcut = \
            r'c:\xxx\sqat\uservalidations\allversions\1.0.0\sqat.lnk'
        self.assertTrue(self.os_module.path.exists(archived_shortcut))

    def test_archive_version__with_validation_files_and_sql_script__shortcut_remains_in_latest(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.sqat.deployer.move_to_archive()
        # Assert
        shortcut_in_latest = \
            r'c:\xxx\sqat\uservalidations\latest\sqat.lnk'
        self.assertTrue(self.os_module.path.exists(shortcut_in_latest))

    def test_archive_version__with_validation_files_and_sql_script__shortcut_target_correct_in_latest(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.sqat.deployer.move_to_archive()
        # Assert
        shortcut_in_latest = \
            r'c:\xxx\sqat\uservalidations\latest\sqat.lnk'
        shortcut_target = self.sqat.validation_deployer.shortcut_examiner.\
            _extract_shortcut_target(shortcut_in_latest)
        self.assertEqual(r'c:\xxx\sqat\candidates\release-1.0.0\validation\sqat.exe', shortcut_target)

    def test_archive_version__with_validation_files_and_sql_script__sql_script_in_archive_folder(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.sqat.deployer.move_to_archive()
        # Assert
        archived_script = \
            r'c:\xxx\sqat\uservalidations\allversions\1.0.0\sqlupdates\script1.sql'
        self.assertTrue(self.os_module.path.exists(archived_script))

    def test_archive_version__with_validation_files_and_sql_script__sql_script_removed_from_next(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_validation_file_in_latest(r'validationfile.txt')
        self.file_builder.add_sql_script_in_next(r'script1.sql')
        self.file_builder.add_shortcut(candidate_dir='release-1.0.0')
        # Act
        self.sqat.deployer.move_to_archive()
        # Assert
        script_path_in_next = \
            r'c:\xxx\sqat\uservalidations\allversions\_next_release\sqlupdates\script1.sql'
        self.assertFalse(self.os_module.path.exists(script_path_in_next))


class FileSystemBuilder:
    def __init__(self, sqat, filesystem):
        self.sqat = sqat
        self.filesystem = filesystem

    def add_file_in_production(self, filename='filename.txt'):
        path = os.path.join(self.sqat.app_paths.production_dir, filename)
        self.filesystem.CreateFile(path)

    def add_file_in_production_config_lab(self, filename='file.txt'):
        path = os.path.join(self.sqat.app_paths.production_config_lab_dir, filename)
        self.filesystem.CreateFile(path)

    def add_file_in_current_candidate_dir(self, filename='file.txt'):
        path = os.path.join(self.sqat.path_properties.current_candidate_dir, filename)
        self.filesystem.CreateFile(path)

    def add_file_in_latest_candidate_dir(self, filename='file.txt'):
        path = os.path.join(self.sqat.path_properties.latest_accepted_candidate_dir, filename)
        print('add file into: {}'.format(path))
        self.filesystem.CreateFile(path)

    def add_validation_file_in_latest(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.sqat.path_properties.latest_validation_files, filename)
        self.filesystem.CreateFile(path, contents=contents)

    def add_validation_file_in_next(self, filename='validationfile.txt', contents=''):
        path = os.path.join(self.sqat.path_properties.next_validation_files, filename)
        print('add file into: {}'.format(path))
        self.filesystem.CreateFile(path, contents=contents)

    def add_sql_script_in_next(self, filename='script1.sql', contents=''):
        path = os.path.join(self.sqat.path_properties.next_sql_updates, filename)
        print('add file into: {}'.format(path))
        self.filesystem.CreateFile(path, contents=contents)

    def add_shortcut(self, candidate_dir='release-1.0.0'):
        cand_path = os.path.join(self.sqat.path_properties.root_candidates, candidate_dir)
        current_shortcut_target = os.path.join(cand_path, r'buildpath\sqat.exe')
        shortcut_save_path = os.path.join(self.sqat.path_properties.user_validations_latest, r'sqat.lnk')
        self.sqat.windows_commands.create_shortcut(shortcut_save_path, current_shortcut_target)
