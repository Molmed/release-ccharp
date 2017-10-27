import unittest
from pyfakefs import fake_filesystem
from release_ccharp.utils import copytree_preserve_existing
from release_ccharp.utils import create_dirs
from tests.unit.utility.fake_os_service import FakeOsService


class TestCopyTree(unittest.TestCase):
    def setUp(self):
        self.filesystem = fake_filesystem.FakeFilesystem()
        self.os_service = FakeOsService(self.filesystem)
        self.source = r'c:\src'
        self.dest = r'c:\dst'
        create_dirs(self.os_service, self.source)
        create_dirs(self.os_service, self.dest)

    def test__with_one_file_in_source_dest_empty__file_copied(self):
        self.filesystem.CreateFile(r'c:\src\file1.txt')
        copytree_preserve_existing(self.os_service, self.source, self.dest)
        self.assertTrue(self.os_service.exists(r'c:\dst\file1.txt'))

    def test__with_two_files_in_source_dest_have_one_file__file_copied(self):
        self.filesystem.CreateFile(r'c:\src\file1.txt')
        self.filesystem.CreateFile(r'c:\src\file2.txt')
        self.filesystem.CreateFile(r'c:\dst\file1.txt')
        copytree_preserve_existing(self.os_service, self.source, self.dest)
        self.assertTrue(self.os_service.exists(r'c:\dst\file2.txt'))

    def test__with_subdir_and_single_file_in_source_dest_empty__file_copied(self):
        create_dirs(self.os_service, r'c:\src\subdir')
        self.filesystem.CreateFile(r'c:\src\subdir\file1.txt')
        copytree_preserve_existing(self.os_service, self.source, self.dest)
        self.assertTrue(self.os_service.exists(r'c:\dst\subdir\file1.txt'))

    def test_complex_with_two_subdirs_in_source_one_exists_in_dest__file_copied(self):
        create_dirs(self.os_service, r'c:\src\subdir1')
        create_dirs(self.os_service, r'c:\src\subdir2')
        create_dirs(self.os_service, r'c:\dst\subdir2')
        self.filesystem.CreateFile(r'c:\src\file1.txt')
        self.filesystem.CreateFile(r'c:\src\subdir1\file2.txt')
        self.filesystem.CreateFile(r'c:\src\subdir1\file3.txt')
        self.filesystem.CreateFile(r'c:\src\subdir2\file4.txt')
        self.filesystem.CreateFile(r'c:\src\subdir2\file5.txt')
        self.filesystem.CreateFile(r'c:\dst\subdir2\file4.txt')
        copytree_preserve_existing(self.os_service, self.source, self.dest)

        self.assertTrue(self.os_service.exists(r'c:\dst\file1.txt'))
        self.assertTrue(self.os_service.exists(r'c:\dst\subdir1\file2.txt'))
        self.assertTrue(self.os_service.exists(r'c:\dst\subdir1\file3.txt'))
        self.assertTrue(self.os_service.exists(r'c:\dst\subdir2\file4.txt'))
        self.assertTrue(self.os_service.exists(r'c:\dst\subdir2\file5.txt'))

    def test__with_file_already_exists_in_destination__file_contents_preserved(self):
        self.filesystem.CreateFile(r'c:\src\file1.txt', contents='new text')
        self.filesystem.CreateFile(r'c:\dst\file1.txt', contents='original text')

        copytree_preserve_existing(self.os_service, self.source, self.dest)

        with self.os_service.open(r'c:\dst\file1.txt', 'r') as f:
            contents = f.read()

        self.assertEqual('original text', contents)
