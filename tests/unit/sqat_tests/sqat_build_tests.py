from __future__ import print_function
import os
from unittest import skip
from release_ccharp.utils import create_dirs
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.exceptions import SnpseqXmlEntryNotFoundException
from release_ccharp.apps.sqat_scripts.builder import SqatConfigXml
from release_ccharp.apps.common.single_file_read_write import StandardVSConfigXML
from tests.unit.sqat_tests.base import SqatBaseTests
from tests.unit.utility.config import SQAT_CONNECT
from tests.unit.utility.config import SQAT_EXE_CONFIG


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

    def test_find_solution_path(self):
        # Arrange
        self.file_builder.add_file_to_application_path('SQAT3.sln')

        # Act
        solution_file_path = self.sqat.builder.solution_file_path

        # Assert
        expected = r'c:\xxx\sqat\candidates\release-1.0.0\gitedvard-sqat-123\application\sqat3.sln'
        self.assertEqual(expected, solution_file_path.lower())

    def test_move_candidates__with_exe_added_to_release__file_copied_to_production(self):
        # Arrange
        self.file_builder.add_file_to_project_root('SQATconfig.xml')
        self.file_builder.add_file_to_project_root('SQATconnect.xml')
        self.file_builder.add_file_to_release('sqat.exe')

        # Act
        self.sqat.builder.move_candidates()

        # Assert
        copied_file = r'c:\xxx\sqat\candidates\release-1.0.0\production\sqat.exe'
        self.assertTrue(self.os_service.exists(copied_file))

    def test_move_candidates__with_exe_added_to_release__file_copied_to_validation(self):
        # Arrange
        self.file_builder.add_file_to_project_root('SQATconfig.xml')
        self.file_builder.add_file_to_project_root('SQATconnect.xml')
        self.file_builder.add_file_to_release('sqat.exe')

        # Act
        self.sqat.builder.move_candidates()

        # Assert
        copied_file = r'c:\xxx\sqat\candidates\release-1.0.0\validation\sqat.exe'
        self.assertTrue(self.os_service.exists(copied_file))

    def test_move_candidates__with_config_file_added_to_project_root__file_copied_to_production(self):
        # Arrange
        self.file_builder.add_file_to_project_root('SQATconfig.xml')
        self.file_builder.add_file_to_project_root('SQATconnect.xml')

        # Act
        self.sqat.builder.move_candidates()

        # Assert
        copied_file = r'c:\xxx\sqat\candidates\release-1.0.0\production\sqatconfig.xml'
        self.assertTrue(self.os_service.exists(copied_file))

    def test_move_candidates__with_connect_file_added_to_project_root__file_copied_to_production(self):
        # Arrange
        self.file_builder.add_file_to_project_root('SQATconfig.xml')
        self.file_builder.add_file_to_project_root('SQATconnect.xml')

        # Act
        self.sqat.builder.move_candidates()

        # Assert
        copied_file = r'c:\xxx\sqat\candidates\release-1.0.0\production\sqatconnect.xml'
        self.assertTrue(self.os_service.exists(copied_file))

    def test_transform_config__with_validation_directory__orig_connect_file_backed_up(self):
        # Arrange
        self.file_builder.add_file_to_validation('sqatconnect.xml', SQAT_CONNECT)
        self.file_builder.add_file_to_production('sqatconnect.xml')

        # Act
        self.sqat.builder._transform_validation_connect_config()

        # Assert
        backed_up_file = r'c:\xxx\sqat\candidates\release-1.0.0\validation\sqatconnect.xml.orig'
        self.assertTrue(self.os_service.exists(backed_up_file))

    def test_transform_config__with_validation_directory__qc_practice_in_connect_file(self):
        # Arrange
        self.file_builder.add_file_to_validation('sqatconnect.xml', SQAT_CONNECT)

        # Act
        self.sqat.builder._transform_validation_connect_config()

        # Assert
        connect_file_path = r'c:\xxx\sqat\candidates\release-1.0.0\validation\sqatconnect.xml'
        with self.sqat.open_xml(connect_file_path) as xml:
            configXml = SqatConfigXml(xml)
            connection_string = configXml.get_connection_string('QC_practice')
            self.assertEqual('data source=mm-wchs001;integrated security=true;initial catalog=QC_practice;',
                             connection_string)

    def test_transform_config__with_validation_directory__qc_devel_in_connect_file(self):
        # Arrange
        self.file_builder.add_file_to_validation('sqatconnect.xml', SQAT_CONNECT)

        # Act
        self.sqat.builder._transform_validation_connect_config()

        # Assert
        connect_file_path = r'c:\xxx\sqat\candidates\release-1.0.0\validation\sqatconnect.xml'
        with self.sqat.open_xml(connect_file_path) as xml:
            configXml = SqatConfigXml(xml)
            connection_string = configXml.get_connection_string('QC_devel')
            self.assertEqual('data source=mm-wchs001;integrated security=true;initial catalog=QC_devel;',
                             connection_string)

    def test_transform_config__with_validation_directory__qc_1_not_in_connect_file(self):
        # Arrange
        self.file_builder.add_file_to_validation('sqatconnect.xml', SQAT_CONNECT)

        # Act
        self.sqat.builder._transform_validation_connect_config()

        # Assert
        connect_file_path = r'c:\xxx\sqat\candidates\release-1.0.0\validation\sqatconnect.xml'
        with self.sqat.open_xml(connect_file_path) as xml:
            configXml = SqatConfigXml(xml)
            with self.assertRaises(SnpseqXmlEntryNotFoundException):
                configXml.get_connection_string('QC_1')

    def test_transform_config__with_production_directory__qc_1_in_connect_file(self):
        # Arrange
        self.file_builder.add_file_to_production('sqatconnect.xml', SQAT_CONNECT)

        # Act
        self.sqat.builder._transform_production_connect_config()

        # Assert
        connect_file_path = r'c:\xxx\sqat\candidates\release-1.0.0\production\sqatconnect.xml'
        with self.sqat.open_xml(connect_file_path) as xml:
            configXml = SqatConfigXml(xml)
            connection_string = configXml.get_connection_string('QC_1')
            self.assertEqual('data source=mm-wchs001;integrated security=true;initial catalog=QC_1;',
                             connection_string)

    def test_transform_config__with_production_directory__qc_devel_not_in_connect_file(self):
        # Arrange
        self.file_builder.add_file_to_production('sqatconnect.xml', SQAT_CONNECT)

        # Act
        self.sqat.builder._transform_production_connect_config()

        # Assert
        connect_file_path = r'c:\xxx\sqat\candidates\release-1.0.0\production\sqatconnect.xml'
        with self.sqat.open_xml(connect_file_path) as xml:
            configXml = SqatConfigXml(xml)
            with self.assertRaises(SnpseqXmlEntryNotFoundException):
                configXml.get_connection_string('QC_devel')

    def test_transform_config__with_production_directory__qc_practice_not_in_connect_file(self):
        # Arrange
        self.file_builder.add_file_to_production('sqatconnect.xml', SQAT_CONNECT)

        # Act
        self.sqat.builder._transform_production_connect_config()

        # Assert
        connect_file_path = r'c:\xxx\sqat\candidates\release-1.0.0\production\sqatconnect.xml'
        with self.sqat.open_xml(connect_file_path) as xml:
            configXml = SqatConfigXml(xml)
            with self.assertRaises(SnpseqXmlEntryNotFoundException):
                configXml.get_connection_string('QC_practice')

    def test_transform_config_vs_xml__with_validation_dir__xml_update_ok(self):
        sqat_config_path = (r'c:\xxx\sqat\candidates\release-1.0.0\validation\sqat.exe.config')
        self.filesystem.CreateFile(sqat_config_path, contents=SQAT_EXE_CONFIG)
        validation_dir = r'c:\xxx\sqat\candidates\release-1.0.0\validation'
        self.sqat.builder._transform_config_vs_xml(validation_dir)
        config_file_path = r'c:\xxx\sqat\candidates\release-1.0.0\validation\sqat.exe.config'
        validation_url = r'http://mm-wchs001:65204/ChiasmaResultServiceValidation/ResultWebService.asmx'
        with self.sqat.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "Molmed.SQAT.Properties")
            self.assertEqual(validation_url,
                             config.get('SNP_Quality_Analysis_Tool_ResultWebServiceDevelopment_ResultWebService'))

    def test_transform_config_vs_xml__with_production_dir__xml_update_ok(self):
        sqat_config_path = (r'c:\xxx\sqat\candidates\release-1.0.0\production\sqat.exe.config')
        self.filesystem.CreateFile(sqat_config_path, contents=SQAT_EXE_CONFIG)
        production_dir = r'c:\xxx\sqat\candidates\release-1.0.0\production'
        self.sqat.builder._transform_config_vs_xml(production_dir)
        config_file_path = r'c:\xxx\sqat\candidates\release-1.0.0\production\sqat.exe.config'
        validation_url = r'http://mm-wchs001:65200/ChiasmaResultService/ResultWebService.asmx'
        with self.sqat.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "Molmed.SQAT.Properties")
            self.assertEqual(validation_url,
                             config.get('SNP_Quality_Analysis_Tool_ResultWebServiceDevelopment_ResultWebService'))

    def test_copy_user_manual__user_manual_in_previous_candidate__user_manual_copied_to_production(self):
        # Arrange
        self.file_builder.add_file_in_previous_candidate('User Manual SNP Quality Analysis Tool.doc')
        create_dirs(self.os_service, r'c:\xxx\sqat\candidates\release-1.0.0\production')

        # Act
        self.sqat.builder.copy_user_manual()

        # Assert
        expected_file = r'c:\xxx\sqat\candidates\release-1.0.0\production\User Manual SNP Quality Analysis Tool.doc'
        self.assertTrue(self.os_service.exists(expected_file))

    def test_copy_user_manual__user_manual_in_previous_candidate__user_manual_copied_to_current_candidate(self):
        # Arrange
        self.file_builder.add_file_in_previous_candidate('User Manual SNP Quality Analysis Tool.doc')
        create_dirs(self.os_service, r'c:\xxx\sqat\candidates\release-1.0.0\production')

        # Act
        self.sqat.builder.copy_user_manual()

        # Assert
        expected_file = r'c:\xxx\sqat\candidates\release-1.0.0\User Manual SNP Quality Analysis Tool.doc'
        self.assertTrue(self.os_service.exists(expected_file))


class FileBuilder:
    def __init__(self, filesystem, os_service):
        self.filesystem = filesystem
        self.os_service = os_service
        self.application_path = r'c:\xxx\sqat\candidates\release-1.0.0\GitEdvard-sqat-123\Application'
        self.project_root_path = r'c:\xxx\sqat\candidates\release-1.0.0\GitEdvard-sqat-123\Application\SQAT3Client'
        self.release_path = \
            r'c:\xxx\sqat\candidates\release-1.0.0\gitedvard-sqat-123\application\sqat3client\bin\release'
        self.validation_path = r'c:\xxx\sqat\candidates\release-1.0.0\validation'
        self.production_path = r'c:\xxx\sqat\candidates\release-1.0.0\production'
        create_dirs(os_service, self.application_path)
        create_dirs(os_service, self.project_root_path)
        create_dirs(os_service, self.release_path)

    def add_file_to_validation(self, filename='file.txt', content=''):
        path = os.path.join(self.validation_path, filename)
        self._log(path)
        self.filesystem.CreateFile(path, contents=content)

    def add_file_to_production(self, filename='file.txt', content=''):
        path = os.path.join(self.production_path, filename)
        self._log(path)
        self.filesystem.CreateFile(path, contents=content)

    def add_file_to_release(self, filename='file.txt', contents=''):
        path = os.path.join(self.release_path, filename)
        self._log(path)
        self.filesystem.CreateFile(path, contents=contents)

    def add_file_to_application_path(self, filename='file.txt', contents=''):
        path = os.path.join(self.application_path, filename)
        self._log(path)
        self.filesystem.CreateFile(path, contents=contents)

    def add_file_to_project_root(self, filename='file.txt', contents=''):
        path = os.path.join(self.project_root_path, filename)
        self._log(path)
        self.filesystem.CreateFile(path, contents=contents)

    def add_file_in_previous_candidate(self, filename='file.txt', contents=''):
        path = os.path.join(r'c:\xxx\sqat\candidates\release-0.0.9', filename)
        self._log(path)
        self.filesystem.CreateFile(path)

    def _log(self, text):
        print('add file into: {}'.format(text))

    def get_contents(self, file_path):
        with self.os_service.open(file_path, 'r') as f:
            c = f.read()
        return c
