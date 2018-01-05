import types
import os

# http://stackoverflow.com/a/3013910/282024
def lazyprop(fn):
    attr_name = '_lazy_' + fn.__name__
    @property
    def _lazyprop(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazyprop


def single(seq):
    """Returns the first element in a list, throwing an exception if there is an unexpected number of items"""
    if isinstance(seq, types.GeneratorType):
        seq = list(seq)
    if len(seq) != 1:
        raise UnexpectedLengthError(
            "Unexpected number of items in the list ({})".format(len(seq)))
    return seq[0]


def single_or_default(seq):
    """Returns the first element in a list or None if the list is empty, raising an exception if
    there are more than one elements in the list"""
    if len(seq) > 1:
        raise UnexpectedLengthError(
            "Expecting at most one item in the list. Got ({}).".format(len(seq)))
    elif len(seq) == 0:
        return None
    else:
        return seq[0]


def create_dirs(os_service, path, whatif=False, log=True):
    if not os_service.exists(path):
        if log:
            print("Create directory: {}".format(path))
        if not whatif:
            os_service.makedirs(path)
    elif log:
        print "Path already exists: {}".format(path)


def copytree_preserve_existing(os_service, src, dst):
    """
    Copy entire file tree from src to dst. If a file with the same name already exists
    in dst, don't overwrite it. If a directory already exists in dst, it's contents will be
    preserved, but there might be new files added into it.
    :param os_service: From this framework (real or fake)
    :param src: Source directory. The top directory is not copied, only it's contents
    :param dst: Destination directory. If it doesn't exists, it will be created.
    :return:
    """
    oss = os_service
    helper = Helpers()
    helper.copy_directory_tree(oss, src, dst)

    file_it = FileIterator(os_service, src)
    for file_sub_path in file_it:
        source_file_path = os.path.join(src, file_sub_path)
        dest_file_path = os.path.join(dst, file_sub_path)
        if not oss.exists(dest_file_path):
            oss.copyfile(source_file_path, dest_file_path)


def copytree_replace_existing(os_service, src, dst):
    """
    Copy entire file tree from src to dst. If a file with the same name already exists
    in dst, don't overwrite it. If a directory already exists in dst, it's contents will be
    preserved, but there might be new files added into it.
    :param os_service: From this framework (real or fake)
    :param src: Source directory. The top directory is not copied, only it's contents
    :param dst: Destination directory. If it doesn't exists, it will be created.
    :return:
    """
    oss = os_service
    helper = Helpers()
    helper.copy_directory_tree(oss, src, dst)

    file_it = FileIterator(oss, src)
    for file_sub_path in file_it:
        source_file_path = os.path.join(src, file_sub_path)
        dest_file_path = os.path.join(dst, file_sub_path)
        oss.copyfile(source_file_path, dest_file_path)


def delete_directory_contents(os_service, folder):
    """
    Removes files and subdirectories in path, but do not remove the top directory
    :param os_service: From this framework (real or fake)
    :param folder:
    :return:
    """
    oss = os_service
    for folder_content in oss.listdir(folder):
        path = os.path.join(folder, folder_content)
        if oss.isfile(path):
            oss.remove_file(path)
        elif oss.isdir(path):
            oss.rmtree(path)


class UnexpectedLengthError(ValueError):
    pass


class FileIterator:
    """
    Iterates files under the given root directory. Return subpaths for the files, anchored at root.
    """
    def __init__(self, os_service, root):
        self.os_service = os_service
        self.root = root

    def __iter__(self):
        return self._traverse(self.root)

    def _traverse(self, dir):
        oss = self.os_service
        for d in oss.listdir(dir):
            sub_directory_cand = os.path.join(dir, d)
            if oss.isdir(sub_directory_cand):
                for x in self._traverse(sub_directory_cand):
                    yield x
            else:
                yield os.path.relpath(sub_directory_cand, self.root)


class DirectoryIterator:
    """
    Iterates directories under the given root directory. Return subpaths for the directory, anchored at root
    """
    def __init__(self, os_service, root):
        self.root = root
        self.os_service = os_service

    def __iter__(self):
        return self._traverse(self.root)

    def _traverse(self, dir):
        oss = self.os_service
        for d in oss.listdir(dir):
            sub_directory_cand = os.path.join(dir, d)
            if oss.isdir(sub_directory_cand):
                yield os.path.relpath(sub_directory_cand, self.root)
                for x in self._traverse(sub_directory_cand):
                    yield x


class Helpers:
    def copy_directory_tree(self, os_service, src, dst):
        oss = os_service
        if not oss.exists(dst):
            oss.makedirs(dst)
        dir_it = DirectoryIterator(oss, src)
        for sub_dir in dir_it:
            dest_dir = os.path.join(dst, sub_dir)
            if not oss.exists(dest_dir):
                oss.makedirs(dest_dir)


class TestIterator:
    def __init__(self):
        self.current = 1

    def create_generator(self):
        while self.current < 5:
            yield self.current
            self.current += 1

    def gen2(self):
        for c in self._rec(0):
            yield c

    def _rec(self, depth):
        if depth < 5:
            yield depth
            for x in self._rec(depth + 1):
                yield x

    def __iter__(self):
        return self._rec(0)
