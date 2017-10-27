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
    if not oss.exists(dst):
        oss.makedirs(dst)
    for d in oss.listdir(src):
        dest_sub_path = os.path.join(dst, d)
        source_sub_path = os.path.join(src, d)
        if oss.isdir(source_sub_path):
            copytree_preserve_existing(oss, source_sub_path, dest_sub_path)
        elif not oss.exists(dest_sub_path):
            oss.copyfile(source_sub_path, dest_sub_path)


class UnexpectedLengthError(ValueError):
    pass
