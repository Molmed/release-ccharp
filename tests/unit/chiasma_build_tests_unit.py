from __future__ import print_function
import unittest
from unittest import skip
from pyfakefs import fake_filesystem
from pyfakefs.fake_filesystem import FakeFileOpen
from release_ccharp.apps.chiasma import Application
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.apps.common import StandardVSConfigXML
from tests.unit.utility.fake_os_service import FakeOsService
from tests.unit.utility.config import CHIASMA_CONFIG
from tests.unit.utility.fake_windows_commands import FakeWindowsCommands


class ChiasmaBuildTests(unittest.TestCase):
    def setUp(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "chiasma",
            "confluence_space_key": "CHI",
            "owner": "GitEdvard"
        }
        branch_provider = FakeBranchProvider()
        wf = SnpseqWorkflow(whatif=False, repo="chiasma")
        wf.config = config
        wf.paths.config = config
        wf.paths.branch_provider = branch_provider

        # Initiate the fake-file system
        self.filesystem = fake_filesystem.FakeFilesystem()
        chiasma_config_path = (r'c:\xxx\chiasma\candidates\validation\chiasma.exe.config')
        self.filesystem.CreateFile(chiasma_config_path, contents=CHIASMA_CONFIG)

        # Instantiate chiasma class (Application)
        os_service = FakeOsService(self.filesystem)
        self.os_module = os_service.os_module
        self.chiasma = Application(wf, branch_provider, os_service,
                                   FakeWindowsCommands(self.filesystem), whatif=False)

    def test__get_version(self):
        version = self.chiasma.branch_provider.candidate_version
        self.assertEqual("1.0.0", version)

    def test__repo_root(self):
        root_path = self.chiasma.path_properties._repo_root
        self.assertEqual(r'c:\xxx\chiasma', root_path)

    def test_replace_assebly_version(self):
        s = """line1
[assembly: AssemblyVersion("1.6.*")]
line 3"""
        (current, new) = self.chiasma.binary_version_updater.get_assembly_replace_strings(s, "1.0.0")
        self.assertEqual("assembly: AssemblyVersion(\"1.6.*\")", current)
        self.assertEqual("assembly: AssemblyVersion(\"1.0.0\")", new)

    def test_read_file(self):
        print(CHIASMA_CONFIG)
        filesystem =  self.chiasma.os_service.filesystem
        file_module = FakeFileOpen(filesystem)
        path = r'c:\xxx\chiasma\candidates\validation\chiasma.exe.config'
        contents = file_module(path)
        print(contents)
        self.assertEqual(1, 1)

    def test_transform_config__with_validation_directory__orig_file_backed_up(self):
        validation_dir = r'c:\xxx\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_config(validation_dir)
        backuped_file = r'c:\xxx\chiasma\candidates\validation\chiasma.exe.config.orig'
        self.assertTrue(self.os_module.path.exists(backuped_file))

    def test_transform_config__with_validation_directory__backed_up_config_one_changed_entry_ok(self):
        validation_dir = r'c:\xxx\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_config(validation_dir)
        config_file_path = r'c:\xxx\chiasma\candidates\validation\chiasma.exe.config.orig'
        with self.chiasma.open_xml(config_file_path, backup_origfile=False) as xml:
            config = StandardVSConfigXML(xml, "Molmed.Chiasma")
            self.assertEqual("False", config.get('DilutePlateAutomaticLabelPrint'))

    def test_transform_config__with_validation_directory__lab_config_exists(self):
        validation_dir = r'c:\xxx\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_config(validation_dir)
        lab_config_file_path = r'c:\xxx\chiasma\candidates\validation\config_lab\chiasma.exe.config'
        self.assertTrue(self.os_module.path.exists(lab_config_file_path))

    def test_transform_config__with_validation_directory__xml_update_ok_in_office_config(self):
        validation_dir = r'c:\xxx\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_config(validation_dir)
        config_file_path = r'c:\xxx\chiasma\candidates\validation\chiasma.exe.config'
        with self.chiasma.open_xml(config_file_path, backup_origfile=False) as xml:
            config = StandardVSConfigXML(xml, "Molmed.Chiasma")
            self.assertEqual("OFFICE", config.get('ApplicationMode'))
            self.assertEqual("600", config.get("RandomProperty"))
            self.assertEqual("True", config.get("DilutePlateAutomaticLabelPrint"))
            self.assertEqual("True", config.get("DiluteTubeAutomaticLabelPrint"))
            self.assertEqual("False", config.get("TestMode"))
            self.assertEqual("GTDB2_practice", config.get("DatabaseName"))
            self.assertEqual("True", config.get("EnforceAppVersion"))
            self.assertEqual("False", config.get("DebugMode"))

    def test_transform_config__with_validation_directory__lab_config_update_ok(self):
        validation_dir = r'c:\xxx\chiasma\candidates\validation'
        self.chiasma.chiasma_builder._transform_config(validation_dir)
        config_file_path = r'c:\xxx\chiasma\candidates\validation\config_lab\chiasma.exe.config'
        with self.chiasma.open_xml(config_file_path, backup_origfile=False) as xml:
            config = StandardVSConfigXML(xml, "Molmed.Chiasma")
            self.assertEqual("LAB", config.get('ApplicationMode'))
            self.assertEqual("600", config.get("RandomProperty"))
            self.assertEqual("True", config.get("DilutePlateAutomaticLabelPrint"))
            self.assertEqual("True", config.get("DiluteTubeAutomaticLabelPrint"))
            self.assertEqual("False", config.get("TestMode"))
            self.assertEqual("GTDB2_practice", config.get("DatabaseName"))
            self.assertEqual("True", config.get("EnforceAppVersion"))
            self.assertEqual("False", config.get("DebugMode"))

    def test_update_binary_version__with_excerp_from_real_file__update_ok(self):
        contents = """row 1
[assembly: AssemblyVersion("1.6.*")]
row3"""
        expected = """row 1
[assembly: AssemblyVersion("1.0.0")]
row3"""
        file_path = (r'c:\xxx\chiasma\candidates\new-candidate\GitEdvard-chiasma-123\chiasma'
                     r'\properties\AssemblyInfo.cs')
        self.filesystem.CreateFile(file_path, contents=contents)
        self.chiasma.chiasma_builder.update_binary_version()
        file_module = FakeFileOpen(self.filesystem)
        with file_module(file_path) as f:
            contents = "".join([line for line in f])
        self.assertEqual(expected, contents)


class FakeBranchProvider:
    def __init__(self):
        self.candidate_version = "1.0.0"
        self.latest_version = "latest-version"
        self.candidate_branch = "new-candidate"