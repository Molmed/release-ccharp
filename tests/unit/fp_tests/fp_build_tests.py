from __future__ import print_function
import os
import re
from unittest import skip
from pyfakefs.fake_filesystem import FakeFileOpen
from release_ccharp.apps.common.single_file_read_write import StandardVSConfigXML
from release_ccharp.utils import create_dirs
from release_ccharp.apps.fp_scripts.builder import ConfigTransformer
from tests.unit.utility.config import FP_CONFIG
from tests.unit.utility.config import FP_CONNECT_CONFIG
from tests.unit.fp_tests.base import FPBaseTests


class FPBuildTests(FPBaseTests):
    def setUp(self):
        self.setup_fp()
        fp_config_path = (r'c:\xxx\fp\candidates\validation\FPDatabase.exe.config')
        self.filesystem.create_file(fp_config_path, contents=FP_CONFIG)
        self.file_builder = FileBuilder(self.filesystem, self.os_service)

    def test_assembly_file_path(self):
        self.file_builder.add_file_to_code_root('assemblyinfo.vb')
        path = r'c:\xxx\fp\candidates\release-1.0.0\gitedvard-fp-123\fpdatabase_sourcecode\assemblyinfo.vb'
        self.assertEqual(path,
                         self.fp.fp_builder._assembly_file_path.lower())

    def test_replace_assembly_version__with_replacing_line_as_last_line__version_number_updated(self):
        s = """line1
<Assembly:  AssemblyVersion("1.0.*")>

"""
        (current, new) = self.fp.binary_version_updater.get_assembly_replace_strings(s, "1.1.0")
        self.assertEqual("Assembly:  AssemblyVersion(\"1.0.*\")", current)
        self.assertEqual("Assembly:  AssemblyVersion(\"1.1.0\")", new)

    def test_file_solution_file(self):
        self.file_builder.add_file_to_code_root('fpdatabase.sln')
        file = self.fp.fp_builder._find_solution_file()
        expected = r'c:\xxx\fp\candidates\release-1.0.0\gitedvard-fp-123\fpdatabase_sourcecode\fpdatabase.sln'
        self.assertEqual(expected, file.lower())

    def test_move_candidates__with_exe_added_to_bin__file_copied_to_production(self):
        # Arrange
        self.file_builder.add_file_to_bin('fpdatabase.exe')
        self.file_builder.add_file_to_code_root('fpdatabaseconfig.txt')

        # Act
        self.fp.fp_builder.move_candidates()

        # Assert
        production_exe_path = r'c:\xxx\fp\candidates\release-1.0.0\production\fpdatabase.exe'
        self.assertTrue(self.os_service.exists(production_exe_path))

    def test_move_candidates__with_exe_added_to_bin__file_copied_to_validation(self):
        # Arrange
        self.file_builder.add_file_to_bin('fpdatabase.exe')
        self.file_builder.add_file_to_code_root('fpdatabaseconfig.txt')

        # Act
        self.fp.fp_builder.move_candidates()

        # Assert
        production_exe_path = r'c:\xxx\fp\candidates\release-1.0.0\validation\fpdatabase.exe'
        self.assertTrue(self.os_service.exists(production_exe_path))

    def test_move_candidates__with_txt_config_added_to_project_root__file_copied_to_validation(self):
        # Arrange
        self.file_builder.add_file_to_code_root('fpdatabaseconfig.txt')

        # Act
        self.fp.fp_builder.move_candidates()

        # Assert
        validation_exe_path = r'c:\xxx\fp\candidates\release-1.0.0\validation\fpdatabaseconfig.txt'
        self.assertTrue(self.os_service.exists(validation_exe_path))

    def test_move_candidates__with_txt_config_added_to_project_root__file_copied_to_production(self):
        # Arrange
        self.file_builder.add_file_to_code_root('fpdatabaseconfig.txt')

        # Act
        self.fp.fp_builder.move_candidates()

        # Assert
        production_exe_path = r'c:\xxx\fp\candidates\release-1.0.0\production\fpdatabaseconfig.txt'
        self.assertTrue(self.os_service.exists(production_exe_path))

    def test_transform_xml_config__with_validation_directory__orig_file_backed_up(self):
        validation_dir = r'c:\xxx\fp\candidates\validation'
        self.config_transformer._transform_xml_config(validation_dir)
        backuped_file = r'c:\xxx\fp\candidates\validation\fpdatabase.exe.config.orig'
        self.assertTrue(self.os_module.path.exists(backuped_file))

    def test_transform_xml_config__with_validation_directory__backed_up_config_one_changed_entry_ok(self):
        validation_dir = r'c:\xxx\fp\candidates\validation'
        self.config_transformer._transform_xml_config(validation_dir)
        config_file_path = r'c:\xxx\fp\candidates\validation\fpdatabase.exe.config.orig'
        with self.fp.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "FPDatabase")
            self.assertEqual("False", config.get('EnforceAppVersion'))

    def test_transform_xml_config__with_validation_directory__xml_update_ok_in_office_config(self):
        validation_dir = r'c:\xxx\fp\candidates\validation'
        self.config_transformer._transform_xml_config(validation_dir)
        config_file_path = r'c:\xxx\fp\candidates\validation\fpdatabase.exe.config'
        with self.fp.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "FPDatabase")
            self.assertEqual("True", config.get("EnforceAppVersion"))

    def test_transform_txt_config_fp_replace(self):
        orig_contents = FP_CONNECT_CONFIG
        new_db_name = 'FP_practice'
        new_contents = self.config_transformer._transform_txt_fp_replace(orig_contents, new_db_name)
        expected = """Tab-delimited configuration file


FPConneCTionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=FP_practice;
ChiasmaConnectionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=GTDB2;  
"""
        self.assertEqual(expected, new_contents)

    def test_transform_txt_config_gtdb2_replace(self):
        orig_contents = """Tab-delimited configuration file


FPConneCTionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=FP_practice;
ChiasmaConnectionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=GTDB2;  
"""
        new_db_name = 'GTDB2_practice'
        new_contents = self.config_transformer._transform_txt_gtdb2_replace(orig_contents, new_db_name)
        expected = """Tab-delimited configuration file


FPConneCTionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=FP_practice;
ChiasmaConnectionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=GTDB2_practice;  
"""
        self.assertEqual(expected, new_contents)

    def test_transform_txt_config__with_validation_directory__update_ok_for_validation(self):
        # Arrange
        fp_config_path = (r'c:\xxx\fp\candidates\validation\FPDatabaseConfig.txt')
        self.filesystem.create_file(fp_config_path, contents=FP_CONNECT_CONFIG)
        validation_dir = r'c:\xxx\fp\candidates\validation'

        # Act
        self.config_transformer._transform_txt_config(validation_dir)

        # Assert
        config_file_path = r'c:\xxx\fp\candidates\validation\fpdatabaseconfig.txt'
        config_contents = self.file_builder.get_contents(config_file_path)
        expected = """Tab-delimited configuration file


FPConneCTionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=FP_practice;
ChiasmaConnectionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=GTDB2_practice;  
"""
        self.assertEqual(expected, config_contents)

    def test_transform_txt_config__with_production_directory__update_ok_for_production(self):
            # Arrange
            fp_config_path = (r'c:\xxx\fp\candidates\release-1.0.0\production\FPDatabaseConfig.txt')
            self.filesystem.create_file(fp_config_path, contents=FP_CONNECT_CONFIG)
            production_dir = r'c:\xxx\fp\candidates\release-1.0.0\production'

            # Act
            self.config_transformer._transform_txt_config(production_dir)

            # Assert
            config_file_path = r'c:\xxx\fp\candidates\release-1.0.0\production\fpdatabaseconfig.txt'
            config_contents = self.file_builder.get_contents(config_file_path)
            expected = """Tab-delimited configuration file


FPConneCTionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=FP;
ChiasmaConnectionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=GTDB2;  
"""
            self.assertEqual(expected, config_contents)

    def test_re_greedy1(self):
        str1 = """hhh_FPConneCTionString_match=1;___match=2
        line2"""
        m = re.match('(^.+FPConneCTionString.*?)match=.+;(.*)', str1, re.IGNORECASE | re.DOTALL)
        expected2 = """___match=2
        line2"""
        self.assertEqual(expected2, m.group(2))

    def test_re_greedy2(self):
        orig_contents = FP_CONNECT_CONFIG
        fp_db_name = 'FP_practice'
        m = re.match('(.*fpconnectionstring.*?);initial catalog.+?;(.*)', orig_contents, re.IGNORECASE | re.DOTALL)
        actual = '{};initial catalog={};{}'.format(m.group(1), fp_db_name, m.group(2))
        expected = """Tab-delimited configuration file


FPConneCTionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=FP_practice;
ChiasmaConnectionString	data source=mm-wchs001;integrated security=SSPI;initial catalog=GTDB2;  
"""
        self.assertEqual(expected, actual)

    def test_re_greedy3(self):
        str1 = """xxx_key1_text_match_
key2_match
line 2
    """
        m = re.match('(.*key1.*?)match(.*)', str1, re.IGNORECASE | re.DOTALL)
        reconstructed = '{}match{}'.format(m.group(1), m.group(2))
        self.assertEqual(str1, reconstructed)
        expected_g1 = """xxx_key1_text_"""
        self.assertEqual(expected_g1, m.group(1))


class FileBuilder:
    def __init__(self, filesystem, os_service):
        self.filesystem = filesystem
        self.os_service = os_service
        self.bin_dir = r'c:\xxx\fp\candidates\release-1.0.0\gitedvard-fp-123\fpdatabase_sourcecode\bin'
        self.code_root_dir = r'c:\xxx\fp\candidates\release-1.0.0\gitedvard-fp-123\fpdatabase_sourcecode'
        create_dirs(os_service, self.code_root_dir)
        create_dirs(os_service, self.bin_dir)

    def add_file_to_bin(self, filename='file.txt', contents=''):
        path = os.path.join(self.bin_dir, filename)
        self._log(path)
        self.filesystem.create_file(path, contents=contents)

    def add_file_to_code_root(self, filename='file.txt', contents=''):
        path = os.path.join(self.code_root_dir, filename)
        self._log(path)
        self.filesystem.create_file(path, contents=contents)

    def _log(self, file_path):
        print('add file into: {}'.format(file_path))

    def get_contents(self, path):
        with self.os_service.open(path, 'r') as f:
            c = f.read()
        return c
