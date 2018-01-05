from __future__ import print_function
import os
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.utils import lazyprop


class SqatBuilder:
    def __init__(self, sqat, os_service, app_paths, file_deployer, binary_version_updater):
        self.sqat = sqat
        self.os_service = os_service
        self.app_paths = app_paths
        self.file_deployer = file_deployer
        self.binary_version_updater = binary_version_updater

    def run(self):
        self.check_not_already_run()
        self.update_binary_version()

    def check_not_already_run(self):
        self.file_deployer.check_not_already_run()

    def update_binary_version(self):
        self.binary_version_updater.update_binary_version(self._assembly_file_path)

    @lazyprop
    def _assembly_file_path(self):
        assembly_file_path = os.path.join(self.sqat.project_root_dir, 'AssemblyInfo.cs')
        if not self.os_service.exists(assembly_file_path):
            raise SnpseqReleaseException(
                "The assembly info file could not be found {}".format(assembly_file_path))
        return assembly_file_path
