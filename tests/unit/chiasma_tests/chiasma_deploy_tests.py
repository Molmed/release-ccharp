import os
from unittest import skip
from release_ccharp.apps.chiasma_scripts.deployer import FileDoesNotExistsException
from tests.unit.chiasma_tests.base import ChiasmaBaseTests


class ChiasmaDeployTests(ChiasmaBaseTests):
    def setUp(self):
        self.base_setup()
        self.file_builder = FileSystemBuilder(self.chiasma, self.filesystem)

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
