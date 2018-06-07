from __future__ import print_function
import os
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.apps.common.single_file_read_write import StandardVSConfigXML
from release_ccharp.utils import create_dirs


class ChiasmaDepositBuilder:
    def __init__(self, chiasma_deposit, file_deployer, app_paths, config):
        self.chiasma_deposit = chiasma_deposit
        self.file_deployer = file_deployer
        self.app_paths = app_paths
        self.config = config

    def run(self):
        self.check_build_not_already_run()
        self.update_binary_version()
        self.build_solution()
        self.move_candidates()
        self.transform_config()

    def update_binary_version(self):
        assembly_file_path = self.app_paths.common_assembly_file_path
        self.chiasma_deposit.binary_version_updater.update_binary_version(assembly_file_path)

    def check_build_not_already_run(self):
        self.file_deployer.check_not_already_run()

    def build_solution(self):
        solution_file = self._find_solution_file()
        solution_file_path = os.path.join(self.chiasma_deposit.app_paths.download_dir, solution_file)
        self.chiasma_deposit.windows_commands.build_solution(solution_file_path)

    def _find_solution_file(self):
        download_dir = self.chiasma_deposit.app_paths.download_dir
        oss = self.chiasma_deposit.os_service
        lst = [o for o in oss.listdir(download_dir) if oss.isfile(os.path.join(download_dir, o))]
        for file in lst:
            if file.endswith(".sln"):
                return file
        raise SnpseqReleaseException("The solution file could not be found, directory {}".format(download_dir))

    def move_candidates(self):
        project_root_path = os.path.join(self.app_paths.download_dir,
                                         self.config['project_root_dir'])
        self.chiasma_deposit.app_paths.common_move_candidates(project_root_path)

    def _transform_config(self, directory):
        config_file_path = os.path.join(directory, self.chiasma_deposit.app_paths.config_file_name)
        db_name = "GTDB2" if directory == self.chiasma_deposit.app_paths.production_dir else "GTDB2_practice"
        self.chiasma_deposit.save_backup_file(config_file_path)
        with self.chiasma_deposit.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "ChiasmaDeposit.Properties")
            config.update("EnforceAppVersion", "True")
            config.update("DatabaseName", db_name)

    def transform_config(self):
        self._transform_config(self.chiasma_deposit.app_paths.production_dir)
        self._transform_config(self.chiasma_deposit.app_paths.validation_dir)
