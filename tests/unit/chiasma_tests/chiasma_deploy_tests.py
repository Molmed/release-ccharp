import os
from unittest import skip
from release_ccharp.apps.common.directory_handling import FileDoesNotExistsException
from tests.unit.chiasma_tests.base import ChiasmaBaseTests


class ChiasmaDeployTests(ChiasmaBaseTests):
    def setUp(self):
        self.base_setup()
        self.file_builder = FileSystemBuilder(self.chiasma, self.filesystem)

    def add_required_files(self):
        self.file_builder.add_file_in_production('chiasma.exe')
        self.file_builder.add_file_in_production('chiasma.exe.config')
        self.file_builder.add_file_in_production_config_lab('chiasma.exe.config')
        self.file_builder.add_file_in_current_candidate_dir('chiasma-user-manual-v1.0.0.pdf')

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

    def test_move_files__with_three_files_in_production__files_exists_in_deploy_catalog(self):
        # Arrange
        self.add_required_files()
        # Act
        self.chiasma.deployer.common_deployer.move_deploy_files()
        # Assert
        exe_path = r'c:\xxx\deploy\chiasma.exe'
        standard_config = r'c:\xxx\deploy\chiasma.exe.config'
        lab_config = r'c:\xxx\deploy\Config_lab\chiasma.exe.config'
        self.assertTrue(self.os_module.path.exists(exe_path))
        self.assertTrue(self.os_module.path.exists(standard_config))
        self.assertTrue(self.os_module.path.exists(lab_config))

    def test_move_user_manual__user_manual_existent__user_manual_moved_to_docs(self):
        # Arrange
        self.add_required_files()
        # Act
        self.chiasma.deployer.common_deployer.move_user_manual()
        # Assert
        user_manaul_path = r'c:\xxx\chiasma\doc\chiasma-user-manual-v1.0.0.pdf'
        self.assertTrue(self.os_module.path.exists(user_manaul_path))

    def test_move_release_history__release_history_exists__release_history_moved(self):
        # Arrange
        self.add_required_files()
        self.file_builder.add_file_in_latest_candidate_dir(r'release-history.txt')
        # Act
        self.chiasma.deployer.common_deployer.copy_release_history()
        # Assert
        release_history = r'c:\xxx\chiasma\doc\release-history.txt'
        self.assertTrue(self.os_module.path.exists(release_history))


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
        self.filesystem.CreateFile(path)

    def add_file_in_latest_candidate_dir(self, filename='file.txt'):
        path = os.path.join(self.chiasma.path_properties.latest_accepted_candidate_dir, filename)
        print('add file into: {}'.format(path))
        self.filesystem.CreateFile(path)
