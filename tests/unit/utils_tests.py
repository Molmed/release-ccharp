import unittest
from unittest import skip
import os
import StringIO
from pyfakefs import fake_filesystem
from release_ccharp.utils import copytree_preserve_existing
from release_ccharp.utils import copytree_replace_existing
from release_ccharp.utils import delete_directory_contents
from release_ccharp.utils import create_dirs
from release_ccharp.utils import DirectoryIterator
from release_ccharp.utils import FileIterator
from release_ccharp.utils import TestIterator
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

    def test__calling_copytree_twice_with_different_dest_directories__files_copied(self):
        create_dirs(self.os_service, r'c:\src\subdir1')
        create_dirs(self.os_service, r'c:\src\subdir2')
        create_dirs(self.os_service, r'c:\src\subdir1\dir1')
        create_dirs(self.os_service, r'c:\src\subdir2\dir2')
        self.filesystem.CreateFile(r'c:\src\subdir1\dir1\file1.txt')
        self.filesystem.CreateFile(r'c:\src\subdir2\dir2\file2.txt')
        source1 = r'c:\src\subdir1'
        source2 = r'c:\src\subdir2'
        copytree_preserve_existing(self.os_service, source1, self.dest)
        copytree_preserve_existing(self.os_service, source2, self.dest)

        self.assertTrue(self.os_service.exists(r'c:\dst\dir1\file1.txt'))
        self.assertTrue(self.os_service.exists(r'c:\dst\dir2\file2.txt'))

    def test__copy_delete_and_copy_with_depth_2_in_source__files_copied(self):
        create_dirs(self.os_service, r'c:\src\dir1\dir2')
        self.filesystem.CreateFile(r'c:\src\dir1\dir2\file.txt')
        copytree_preserve_existing(self.os_service, self.source, self.dest)

        self.assertTrue(self.os_service.exists(r'c:\dst\dir1\dir2\file.txt'))

        delete_directory_contents(self.os_service, r'c:\dst\dir1')

        copytree_preserve_existing(self.os_service, self.source, self.dest)

        self.assertTrue(self.os_service.exists(r'c:\dst\dir1\dir2\file.txt'))

    def test__copy_to_non_existent_folder__files_copied(self):
        self.filesystem.CreateFile(r'c:\src\file.txt')
        dest = r'c:\dst\dir1'
        copytree_preserve_existing(self.os_service, self.source, dest)

        self.assertTrue(self.os_service.exists(r'c:\dst\dir1\file.txt'))


class TestDeleteDirectoryContents(unittest.TestCase):
    def setUp(self):
        self.filesystem = fake_filesystem.FakeFilesystem()
        self.os_service = FakeOsService(self.filesystem)
        self.file1 = r'c:\path1\file1.txt'
        self.file2 = r'c:\path1\path2\file2.txt'
        self.another_folder = r'c:\anotherfolder'
        self.filesystem.CreateFile(self.file1)
        self.filesystem.CreateFile(self.file2)
        create_dirs(self.os_service, self.another_folder)

    def test_doing_nothing__file1_exists(self):
        self.assertTrue(self.os_service.exists(self.file1))

    def test_remove_path1__file1_is_gone(self):
        delete_directory_contents(self.os_service, r'c:\path1')
        self.assertFalse(self.os_service.exists(self.file1))

    def test_remove_path1__file2_is_gone(self):
        delete_directory_contents(self.os_service, r'c:\path1')
        self.assertFalse(self.os_service.exists(self.file2))

    def test_remove_path1__anotherfolder_exists(self):
        delete_directory_contents(self.os_service, r'c:\path1')
        self.assertTrue(self.os_service.exists(self.another_folder))


class TestCopytreeReplaceExisting(unittest.TestCase):
    def setUp(self):
        self.filesystem = fake_filesystem.FakeFilesystem()
        self.os_service = FakeOsService(self.filesystem)
        self.source = r'c:\src'
        self.dest = r'c:\dst'
        create_dirs(self.os_service, self.source)
        create_dirs(self.os_service, self.dest)

    def test__with_one_file_in_source_dest_empty__file_copied(self):
        self.filesystem.CreateFile(r'c:\src\file1.txt')
        copytree_replace_existing(self.os_service, self.source, self.dest)
        self.assertTrue(self.os_service.exists(r'c:\dst\file1.txt'))

    def test__with_one_file_in_source_dest_have_same_file__file_replaced(self):
        self.filesystem.CreateFile(r'c:\src\file1.txt', contents='source')
        self.filesystem.CreateFile(r'c:\dst\file1.txt', contents='destination')
        copytree_replace_existing(self.os_service, self.source, self.dest)
        with self.os_service.open(r'c:\dst\file1.txt', 'r') as f:
            c = f.read()
        self.assertEqual('source', c)

    def test__with_one_file_in_source_dest_have_two_files__extra_file_in_dest_untoutched(self):
        self.filesystem.CreateFile(r'c:\src\file1.txt')
        self.filesystem.CreateFile(r'c:\dst\file1.txt')
        self.filesystem.CreateFile(r'c:\dst\file2.txt', contents='destination')
        copytree_replace_existing(self.os_service, self.source, self.dest)
        with self.os_service.open(r'c:\dst\file2.txt', 'r') as f:
            c = f.read()
        self.assertEqual('destination', c)

    def test__with_two_subdirs_in_source_one_common_file__source_exclusive_copied(self):
        # Arrange
        create_dirs(self.os_service, r'c:\src\subdir1')
        create_dirs(self.os_service, r'c:\src\subdir2')
        create_dirs(self.os_service, r'c:\dst\subdir2')
        self.filesystem.CreateFile(r'c:\src\source_exclusive1.txt')
        self.filesystem.CreateFile(r'c:\src\subdir1\source_exclusive2.txt')
        self.filesystem.CreateFile(r'c:\src\subdir1\source_exclusive3.txt')
        self.filesystem.CreateFile(r'c:\src\subdir2\common.txt')
        self.filesystem.CreateFile(r'c:\src\subdir2\source_exclusive4.txt')
        self.filesystem.CreateFile(r'c:\dst\subdir2\common.txt')
        self.filesystem.CreateFile(r'c:\dst\subdir2\dst_exclusive', contents='destination')

        # Act
        copytree_replace_existing(self.os_service, self.source, self.dest)

        # Assert
        self.assertTrue(self.os_service.exists(r'c:\dst\source_exclusive1.txt'))
        self.assertTrue(self.os_service.exists(r'c:\dst\subdir1\source_exclusive2.txt'))
        self.assertTrue(self.os_service.exists(r'c:\dst\subdir1\source_exclusive3.txt'))
        self.assertTrue(self.os_service.exists(r'c:\dst\subdir2\source_exclusive4.txt'))

    def test__with_two_subdirs_in_source_one_common_file__dest_exclusive_preserved(self):
        # Arrange
        create_dirs(self.os_service, r'c:\src\subdir1')
        create_dirs(self.os_service, r'c:\src\subdir2')
        create_dirs(self.os_service, r'c:\dst\subdir2')
        self.filesystem.CreateFile(r'c:\src\source_exclusive1.txt')
        self.filesystem.CreateFile(r'c:\src\subdir1\source_exclusive2.txt')
        self.filesystem.CreateFile(r'c:\src\subdir1\source_exclusive3.txt')
        self.filesystem.CreateFile(r'c:\src\subdir2\common.txt')
        self.filesystem.CreateFile(r'c:\src\subdir2\source_exclusive4.txt')
        self.filesystem.CreateFile(r'c:\dst\subdir2\common.txt')
        self.filesystem.CreateFile(r'c:\dst\subdir2\dst_exclusive.txt', contents='destination')

        # Act
        copytree_replace_existing(self.os_service, self.source, self.dest)

        # Assert
        with self.os_service.open(r'c:\dst\subdir2\dst_exclusive.txt', 'r') as f:
            c = f.read()
        self.assertEqual("destination", c)

    def test__with_two_subdirs_in_source_one_common_file__common_file_replaced(self):
        # Arrange
        create_dirs(self.os_service, r'c:\src\subdir1')
        create_dirs(self.os_service, r'c:\src\subdir2')
        create_dirs(self.os_service, r'c:\dst\subdir2')
        self.filesystem.CreateFile(r'c:\src\source_exclusive1.txt')
        self.filesystem.CreateFile(r'c:\src\subdir1\source_exclusive2.txt')
        self.filesystem.CreateFile(r'c:\src\subdir1\source_exclusive3.txt')
        self.filesystem.CreateFile(r'c:\src\subdir2\common.txt', contents='source')
        self.filesystem.CreateFile(r'c:\src\subdir2\source_exclusive4.txt')
        self.filesystem.CreateFile(r'c:\dst\subdir2\common.txt', contents='destination')
        self.filesystem.CreateFile(r'c:\dst\subdir2\dst_exclusive.txt', contents='destination')

        # Act
        copytree_replace_existing(self.os_service, self.source, self.dest)

        # Assert
        with self.os_service.open(r'c:\dst\subdir2\common.txt', 'r') as f:
            c = f.read()
        self.assertEqual("source", c)


class TestIterators(unittest.TestCase):
    def setUp(self):
        self.filesystem = fake_filesystem.FakeFilesystem()
        self.os_service = FakeOsService(self.filesystem)
        self.root = r'c:\root'
        self.filesystem_builder = FileSystemBuilder(self.os_service, self.filesystem)
        create_dirs(self.os_service, self.root)

    def test_directory_iterator__with_no_subdirectories__zero_iterations(self):
        # Arrange
        dir_it = DirectoryIterator(self.os_service, self.root)

        # Act
        gen = (d for d in dir_it)
        directories = list(gen)

        # Assert
        self.assertEqual(0, len(directories))

    def test_directory_iterator__with_one_subdirectory__one_iteration(self):
        # Arrange
        create_dirs(self.os_service, r'c:\root\subdir1')
        dir_it = DirectoryIterator(self.os_service, self.root)

        # Act
        gen = (d for d in dir_it)
        directories = list(gen)

        # Assert
        self.assertEqual(1, len(directories))

    def test_directory_iterator__with_one_subdirectory__iteration_result_ok(self):
        # Arrange
        create_dirs(self.os_service, r'c:\root\subdir1')
        dir_it = DirectoryIterator(self.os_service, self.root)

        # Act
        gen = (d for d in dir_it)
        directories = list(gen)

        # Assert
        self.assertEqual(r'subdir1', directories[0])

    def test_directory_iterator__with_two_subdirectories_depth_1__two_iterations(self):
        # Arrange
        create_dirs(self.os_service, r'c:\root\subdir1')
        create_dirs(self.os_service, r'c:\root\subdir2')
        dir_it = DirectoryIterator(self.os_service, self.root)

        # Act
        gen = (d for d in dir_it)
        directories = list(gen)

        # Assert
        self.assertEqual(2, len(directories))

    def test_directory_iterator__with_two_subdirectories_depth_1__iteration_results_ok(self):
        # Arrange
        create_dirs(self.os_service, r'c:\root\subdir1')
        create_dirs(self.os_service, r'c:\root\subdir2')
        dir_it = DirectoryIterator(self.os_service, self.root)

        # Act
        gen = dir_it
        directories = sorted(list(gen))

        # Assert
        self.assertEqual('subdir1', directories[0])
        self.assertEqual('subdir2', directories[1])

    def test_directory_iterator__with_two_subdirectories_depth_2__two_iterations(self):
        # Arrange
        create_dirs(self.os_service, r'c:\root\subdir1')
        create_dirs(self.os_service, r'c:\root\subdir1\subdir2')
        dir_it = DirectoryIterator(self.os_service, self.root)

        # Act
        directories = list(dir_it)

        # Assert
        self.assertEqual(2, len(directories))

    def test_directory_iterator__with_two_subdirectories_depth_2__iteration_results_ok(self):
        # Arrange
        create_dirs(self.os_service, r'c:\root\subdir1')
        create_dirs(self.os_service, r'c:\root\subdir1\subdir2')
        dir_it = DirectoryIterator(self.os_service, self.root)

        # Act
        directories = sorted(list(dir_it))

        # Assert
        self.assertEqual(r'subdir1', directories[0])
        self.assertEqual(r'subdir1\subdir2', directories[1])

    def test_directory_iterator__with_depth_2_with_4__six_iterations(self):
        # Arrange
        create_dirs(self.os_service, r'c:\root\subdir1')
        create_dirs(self.os_service, r'c:\root\subdir1\subdir2')
        create_dirs(self.os_service, r'c:\root\subdir1\subdir3')
        create_dirs(self.os_service, r'c:\root\subdir4')
        create_dirs(self.os_service, r'c:\root\subdir4\subdir5')
        create_dirs(self.os_service, r'c:\root\subdir4\subdir6')
        dir_it = DirectoryIterator(self.os_service, self.root)

        # Act
        directories = list(dir_it)

        # Assert
        self.assertEqual(6, len(directories))

    def test_file_iterator__with_one_single_file__returns_subpath(self):
        # Arrange
        self.filesystem.CreateFile(r'c:\root\file1.txt')
        file_it = FileIterator(self.os_service, self.root)

        # Act
        files = list(file_it)

        # Assert
        self.assertEqual(r'file1.txt', files[0])

    def test_file_iterator__with_file_in_subdir__returns_subpath(self):
        # Arrange
        self.filesystem.CreateFile(r'c:\root\subdir\file1.txt')
        file_it = FileIterator(self.os_service, self.root)

        # Act
        files = list(file_it)

        # Assert
        self.assertEqual(r'subdir\file1.txt', files[0])


class TestTestIterator(unittest.TestCase):
    def test_generator(self):
        it = TestIterator()
        for c in it.create_generator():
            print(c)
        # lst = list(it.create_generator())
        # print(lst[0])
        self.assertEqual(2, 2)

    def test_recursive_gen(self):
        it = TestIterator()
        for c in it.gen2():
            print(c)
        self.assertEqual(5, len(list(it.gen2())))

    def test_iteration(self):
        it = TestIterator()

        lst = list(it)

        self.assertEqual(5, len(lst))


class TestStreamHandling(unittest.TestCase):
    def setUp(self):
        self.filesystem = fake_filesystem.FakeFilesystem()
        self.os_service = FakeOsService(self.filesystem)
        self.source = r'c:\src'
        create_dirs(self.os_service, self.source)


    def test_stringio__call_read__returns_string(self):
        buffer = StringIO.StringIO()
        buffer.write('hej')
        buffer.seek(0)
        c = buffer.read()
        self.assertEqual('hej', c)

    def test_stringio__call_read_n_one_time__returns_first_n_chars(self):
        buffer = StringIO.StringIO()
        buffer.write('hej')
        buffer.seek(0)
        c = buffer.read(2)
        self.assertEqual('he', c)

    def test_stringio__call_read_n_two_times__returns_second_chunk_of_chars(self):
        buffer = StringIO.StringIO()
        buffer.write('hej')
        buffer.seek(0)
        c = buffer.read(2)
        c = buffer.read(2)
        self.assertEqual('j', c)

    def test_fake_os_service_open__with_fake_file_with_contents__contents_is_read(self):
        self.filesystem.CreateFile(r'c:\src\file.txt', contents='contents')
        with self.os_service.open(r'c:\src\file.txt', 'r') as f:
            c = f.read()
        self.assertEqual('contents', c)


class FileSystemBuilder():
    def __init__(self, os_service, filesystem):
        self.os_service = os_service
        self.filesystem = filesystem

    def get_contents(self, path):
        with self.os_service.open(path, 'r') as f:
            c = f.read()
        return c