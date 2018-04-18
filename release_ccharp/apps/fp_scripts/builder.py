from __future__ import print_function
import os
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.apps.common.single_file_read_write import StandardVSConfigXML
from release_ccharp.utils import create_dirs


class FPBuilder:
    def __init__(self, fp, file_deployer, app_paths, config, os_service):
        self.fp = fp
        self.file_deployer = file_deployer
        self.app_paths = app_paths
        self.os_service = os_service
        self.config = config

    def run(self):
        self.check_build_not_already_run()
        self.update_binary_version()

    def check_build_not_already_run(self):
        self.file_deployer.check_not_already_run()

    def update_binary_version(self):
        assembly_file_path = self._assembly_file_path
        self.fp.binary_version_updater.update_binary_version(assembly_file_path)

    @property
    def _assembly_file_path(self):
        assembly_subpath = os.path.join(self.config["project_root_dir"], 'assemblyinfo.vb')
        assembly_file_path = os.path.join(
            self.app_paths.download_dir, assembly_subpath)
        print('file path: {}'.format(assembly_file_path))
        if not self.os_service.exists(assembly_file_path):
            raise SnpseqReleaseException(
                "The assembly info file could not be found {}".format(assembly_file_path))
        return assembly_file_path


