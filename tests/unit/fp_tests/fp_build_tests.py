from __future__ import print_function
import os
from unittest import skip
from pyfakefs.fake_filesystem import FakeFileOpen
from release_ccharp.apps.common.single_file_read_write import StandardVSConfigXML
from release_ccharp.utils import create_dirs
from tests.unit.utility.config import FP_CONFIG
from tests.unit.fp_tests.base import FPBaseTests


class FPBuildTests(FPBaseTests):
    def setUp(self):
        self.setup_fp()
        fp_config_path = (r'c:\xxx\fp\candidates\validation\FPDatabase.exe.config')
        self.filesystem.CreateFile(fp_config_path, contents=FP_CONFIG)
        self.file_builder = FileBuilder(self.filesystem, self.os_service)

    def test_assembly_file_path(self):
        path = r'c:\xxx\fp\candidates\release-1.0.0\gitedvard-fp-123\fpdatabase_sourcecode\assemblyinfo.vb'
        self.filesystem.CreateFile(path)
        self.assertEqual(path,
                         self.fp.fp_builder._assembly_file_path.lower())

    #@skip('wip')
    def test_replace_assembly_version__with_replacing_line_as_last_line__version_number_updated(self):
        s = """line1
<Assembly:  AssemblyVersion("1.0.*")>

"""
        (current, new) = self.fp.binary_version_updater.get_assembly_replace_strings(s, "1.1.0")
        self.assertEqual("Assembly:  AssemblyVersion(\"1.0.*\")", current)
        self.assertEqual("Assembly:  AssemblyVersion(\"1.1.0\")", new)


class FileBuilder:
    def __init__(self, filesystem, os_service):
        self.filesystem = filesystem
        self.release_dir = r'c:\xxx\fp\candidates\release-1.0.0\gitedvard-fp-123\fp\bin\release'
        create_dirs(os_service, self.release_dir)

    def add_file_to_release(self, filename='file.txt', contents=''):
        path = os.path.join(self.release_dir, filename)
        self._log(path)
        self.filesystem.CreateFile(path, contents=contents)

    def _log(self, file_path):
        print('add file into: {}'.format(file_path))
