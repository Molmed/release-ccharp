from __future__ import print_function
import os
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.utils import lazyprop


class SqatBuilder:
    def __init__(self, sqat, os_service, app_paths, file_deployer, binary_version_updater, windows_commands):
        self.sqat = sqat
        self.os_service = os_service
        self.app_paths = app_paths
        self.file_deployer = file_deployer
        self.binary_version_updater = binary_version_updater
        self.windows_commands = windows_commands

    def run(self):
        self.check_not_already_run()
        self.update_binary_version()
        self.build_solution()

    def check_not_already_run(self):
        self.file_deployer.check_not_already_run()

    def update_binary_version(self):
        self.binary_version_updater.update_binary_version(self._assembly_file_path)

    def build_solution(self):
        self.windows_commands.build_solution(self.solution_file_path)

    @lazyprop
    def _assembly_file_path(self):
        assembly_file_path = os.path.join(self.sqat.project_root_dir, 'AssemblyInfo.cs')
        if not self.os_service.exists(assembly_file_path):
            raise SnpseqReleaseException(
                "The assembly info file could not be found {}".format(assembly_file_path))
        return assembly_file_path

    def _find_solution_file_name(self):
        application = self._application_path
        oss = self.os_service
        lst = [o for o in oss.listdir(application) if oss.isfile(os.path.join(application, o))]
        for file in lst:
            if file.endswith(".sln"):
                return file
        raise SnpseqReleaseException("The solution file could not be found, directory {}".format(application))

    @lazyprop
    def solution_file_path(self):
        return os.path.join(self._application_path, self._find_solution_file_name())

    @lazyprop
    def _application_path(self):
        download_dir = self.app_paths.download_dir
        return os.path.join(download_dir, 'application')
