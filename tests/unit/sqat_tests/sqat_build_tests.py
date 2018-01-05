from __future__ import print_function
import os
from unittest import skip
from release_ccharp.utils import create_dirs
from release_ccharp.exceptions import SnpseqReleaseException
from tests.unit.sqat_tests.base import SqatBaseTests


class SqatBuildTests(SqatBaseTests):
    def setUp(self):
        self.setup_sqat()
        self.file_builder = FileBuilder(self.filesystem, self.os_service)
        create_dirs(self.os_service, self.file_builder.application_path)

    def test_check_not_already_run__with_production_catalog_existing__throws(self):
        # Arrange
        create_dirs(self.os_service, r'c:\xxx\sqat\candidates\release-1.0.0\production')

        # Act
        # Assert
        with self.assertRaises(SnpseqReleaseException):
            self.sqat.builder.check_not_already_run()

    def test_update_binary_version_replace_strings__current_file_has_version_3_2__replaced_with_1_0(self):
        s = """line1
[assembly: AssemblyVersion("3.2.*")]
line 3"""
        (current, new) = self.sqat.builder.binary_version_updater.get_assembly_replace_strings(s, "1.0.0")
        self.assertEqual("assembly: AssemblyVersion(\"3.2.*\")", current)
        self.assertEqual("assembly: AssemblyVersion(\"1.0.0\")", new)

    def test_assembly_file_path__with_initiation_as_reality__assembly_file_path_as_expected(self):
        # Arrange
        self.file_builder.add_file_to_project_root('AssemblyInfo.cs')
        # Act
        actual_assembly_info_path = self.sqat.builder._assembly_file_path.lower()

        # Assert
        expected = r'c:\xxx\sqat\candidates\release-1.0.0\gitedvard-sqat-123\application\sqat3client\assemblyinfo.cs'
        self.assertEqual(expected, actual_assembly_info_path)

    def test_binary_version_updater__with_assembly_file_has_version_3_2__replaced_with_1_0(self):
        # Arrange
        s = """line1
[assembly: AssemblyVersion("3.2.*")]
line 3"""
        self.file_builder.add_file_to_project_root('AssemblyInfo.cs', contents=s)

        # Act
        self.sqat.builder.update_binary_version()

        # Assert
        file_path = os.path.join(self.file_builder.project_root_path, 'AssemblyInfo.cs')
        c = self.file_builder.get_contents(file_path)
        expected = ('line1\n'
                    '[assembly: AssemblyVersion("1.0.0")]\n'
                    'line 3')
        self.assertEqual(expected, c)



class FileBuilder:
    def __init__(self, filesystem, os_service):
        self.filesystem = filesystem
        self.os_service = os_service
        self.application_path = r'c:\xxx\sqat\candidates\release-1.0.0\GitEdvard-sqat-123\Application'
        self.project_root_path = r'c:\xxx\sqat\candidates\release-1.0.0\GitEdvard-sqat-123\Application\SQAT3Client'

    def add_file_to_application_path(self, filename='file.txt', contents=''):
        path = os.path.join(self.application_path, filename)
        self._log(path)
        self.filesystem.CreateFile(path, contents=contents)

    def add_file_to_project_root(self, filename='file.txt', contents=''):
        path = os.path.join(self.project_root_path, filename)
        self._log(path)
        self.filesystem.CreateFile(path, contents=contents)

    def _log(self, text):
        print('add file into: {}'.format(text))

    def get_contents(self, file_path):
        with self.os_service.open(file_path, 'r') as f:
            c = f.read()
        return c
