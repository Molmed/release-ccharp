from __future__ import print_function
import os
from unittest import skip
import pytest
from pyfakefs.fake_filesystem import FakeFileOpen
from release_ccharp.apps.common.single_file_read_write import StandardVSConfigXML
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.utils import create_dirs
from tests.unit.utility.config import CHIASMA_CONFIG
from tests.unit.utility.config import CHIASMA_SHAREDKERNEL_CONFIG
from tests.unit.chiasma_tests.base import ChiasmaBaseTests


class ChiasmaBuildTests(ChiasmaBaseTests):
    def setUp(self):
        self.setup_chiasma()
        chiasma_config_path = (r'c:\local\chiasma\candidates\validation\chiasma.exe.config')
        shared_kernel_config_path = (r'c:\local\chiasma\candidates\validation\chiasma.sharedkernel.exe.config')
        self.filesystem.create_file(chiasma_config_path, contents=CHIASMA_CONFIG)
        self.filesystem.create_file(shared_kernel_config_path, contents=CHIASMA_SHAREDKERNEL_CONFIG)
        self.file_builder = FileBuilder(self.filesystem, self.os_service)

    def test__get_version(self):
        version = self.chiasma.branch_provider.candidate_version
        self.assertEqual("1.0.0", version)

    def test__repo_root(self):
        root_path = self.chiasma.local_path_properties._repo_root
        self.assertEqual(r'c:\local\chiasma', root_path)

    def test_replace_assebly_version(self):
        s = """line1
[assembly: AssemblyVersion("1.6.*")]
line 3"""
        (current, new) = self.chiasma.binary_version_updater.get_assembly_replace_strings(s, "1.0.0")
        self.assertEqual("assembly: AssemblyVersion(\"1.6.*\")", current)
        self.assertEqual("assembly: AssemblyVersion(\"1.0.0\")", new)

    def test_production_folder_exists_render_error_message(self):
        self.filesystem.create_file(r'c:\local\chiasma\candidates\release-1.0.0\production\chiasma.exe')
        with self.assertRaises(SnpseqReleaseException):
            self.chiasma.chiasma_builder.check_build_not_already_run()

    def test_read_file(self):
        print(CHIASMA_CONFIG)
        filesystem =  self.chiasma.os_service.filesystem
        file_module = FakeFileOpen(filesystem)
        path = r'c:\local\chiasma\candidates\validation\chiasma.exe.config'
        contents = file_module(path)
        print(contents)
        self.assertEqual(1, 1)

    def test_move_candidates__with_exe_added_to_release__file_copied_to_production(self):
        # Arrange
        self.file_builder.add_file_to_release('chiasma.exe')

        # Act
        self.chiasma.chiasma_builder.move_candidates()

        # Assert
        production_exe_path = r'c:\local\chiasma\candidates\release-1.0.0\production\chiasma.exe'
        self.assertTrue(self.os_service.exists(production_exe_path))

    def test_move_candidates__with_exe_added_to_release__file_copied_to_validation(self):
        # Arrange
        self.file_builder.add_file_to_release('chiasma.exe')

        # Act
        self.chiasma.chiasma_builder.move_candidates()

        # Assert
        validation_exe_path = r'c:\local\chiasma\candidates\release-1.0.0\validation\chiasma.exe'
        self.assertTrue(self.os_service.exists(validation_exe_path))

    def test_transform_config__with_validation_directory__orig_file_backed_up(self):
        validation_dir = r'c:\local\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_configs(validation_dir)
        backuped_file = r'c:\local\chiasma\candidates\validation\chiasma.exe.config.orig'
        self.assertTrue(self.os_module.path.exists(backuped_file))

    def test_transform_config__with_validation_directory__backed_up_config_one_changed_entry_ok(self):
        validation_dir = r'c:\local\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_configs(validation_dir)
        config_file_path = r'c:\local\chiasma\candidates\validation\chiasma.exe.config.orig'
        with self.chiasma.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "Molmed.Chiasma.Properties")
            self.assertEqual("False", config.get('DilutePlateAutomaticLabelPrint'))

    def test_transform_config__with_validation_directory__lab_config_exists(self):
        validation_dir = r'c:\local\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_configs(validation_dir)
        lab_config_file_path = r'c:\local\chiasma\candidates\validation\config_lab\chiasma.exe.config'
        self.assertTrue(self.os_module.path.exists(lab_config_file_path))

    def test_transform_config__with_validation_directory__xml_update_ok_in_office_config(self):
        validation_dir = r'c:\local\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_configs(validation_dir)
        config_file_path = r'c:\local\chiasma\candidates\validation\chiasma.exe.config'
        with self.chiasma.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "Molmed.Chiasma.Properties")
            self.assertEqual("OFFICE", config.get('ApplicationMode'))
            self.assertEqual("600", config.get("RandomProperty"))
            self.assertEqual("True", config.get("DilutePlateAutomaticLabelPrint"))
            self.assertEqual("True", config.get("DiluteTubeAutomaticLabelPrint"))
            self.assertEqual("False", config.get("TestMode"))
            self.assertEqual("True", config.get("EnforceAppVersion"))
            self.assertEqual("False", config.get("DebugMode"))
            self.assertEqual("Ef", config.get("RepositoryImplementation"))

    def test_transform_config_for_shared_kernel__with_validation_dir__xml_update_ok(self):
        validation_dir = r'c:\local\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_configs(validation_dir)
        config_file_path = r'c:\local\chiasma\candidates\validation\chiasma.sharedkernel.exe.config'
        with self.chiasma.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "Chiasma.SharedKernel.Properties")
            self.assertEqual("GTDB2_practice", config.get("DatabaseName"))
            self.assertEqual("ProjectMan_devel", config.get("ProjmanDatabaseName"))

    def test_transform_config__with_validation_directory__lab_config_update_ok(self):
        validation_dir = r'c:\local\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_configs(validation_dir)
        config_file_path = r'c:\local\chiasma\candidates\validation\config_lab\chiasma.exe.config'
        with self.chiasma.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "Molmed.Chiasma.Properties")
            self.assertEqual("LAB", config.get('ApplicationMode'))
            self.assertEqual("600", config.get("RandomProperty"))
            self.assertEqual("True", config.get("DilutePlateAutomaticLabelPrint"))
            self.assertEqual("True", config.get("DiluteTubeAutomaticLabelPrint"))
            self.assertEqual("False", config.get("TestMode"))
            self.assertEqual("True", config.get("EnforceAppVersion"))
            self.assertEqual("False", config.get("DebugMode"))
            self.assertEqual("Ef", config.get("RepositoryImplementation"))

    def test_transform_shared_kernel_config__with_validation_directory__lab_config_update_ok(self):
        validation_dir = r'c:\local\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_configs(validation_dir)
        # Note, shared kernel config is not in lab-config dir!
        config_file_path = r'c:\local\chiasma\candidates\validation\chiasma.sharedkernel.exe.config'
        with self.chiasma.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "Chiasma.SharedKernel.Properties")
            self.assertEqual("GTDB2_practice", config.get("DatabaseName"))
            self.assertEqual("ProjectMan_devel", config.get("ProjmanDatabaseName"))

    def test_update_binary_version__with_excerp_from_real_file__update_ok(self):
        original_contents = """row 1
[assembly: AssemblyVersion("1.6.*")]
row3"""
        expected = """row 1
[assembly: AssemblyVersion("1.0.0")]
row3"""
        file_path = (r'c:\local\chiasma\candidates\release-1.0.0\GitEdvard-chiasma-123\chiasma'
                     r'\properties\AssemblyInfo.cs')
        self.filesystem.create_file(file_path, contents=original_contents)
        self.chiasma.chiasma_builder.update_binary_version()
        file_module = FakeFileOpen(self.filesystem)
        with file_module(file_path) as f:
            contents = "".join([line for line in f])
        self.assertEqual(expected, contents)


class FileBuilder:
    def __init__(self, filesystem, os_service):
        self.filesystem = filesystem
        self.release_dir = r'c:\local\chiasma\candidates\release-1.0.0\gitedvard-chiasma-123\chiasma\bin\release'
        create_dirs(os_service, self.release_dir)

    def add_file_to_release(self, filename='file.txt', contents=''):
        path = os.path.join(self.release_dir, filename)
        self._log(path)
        self.filesystem.create_file(path, contents=contents)

    def _log(self, file_path):
        print('add file into: {}'.format(file_path))
