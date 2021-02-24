from __future__ import print_function
import os
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.apps.common.single_file_read_write import VsConfigOpener
from release_ccharp.utils import create_dirs


class OrderBuilder:
    def __init__(self, order, file_deployer, app_paths, config):
        self.order = order
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
        self.order.binary_version_updater.update_binary_version(assembly_file_path)

    def check_build_not_already_run(self):
        self.file_deployer.check_not_already_run()

    def build_solution(self):
        solution_file = self._find_solution_file()
        solution_file_path = os.path.join(self.order.app_paths.download_dir, solution_file)
        self.order.windows_commands.build_solution(solution_file_path)

    def _find_solution_file(self):
        download_dir = self.order.app_paths.download_dir
        lst = [o for o in os.listdir(download_dir) if os.path.isfile(os.path.join(download_dir, o))]
        for file in lst:
            if file.endswith(".sln"):
                return file
        raise SnpseqReleaseException("The solution file could not be found, directory {}".format(download_dir))

    def move_candidates(self):
        project_root_path = os.path.join(self.app_paths.download_dir,
                                         self.config['project_root_dir'])
        self.order.app_paths.common_move_candidates(project_root_path)

    def _transform_config(self, directory, db_name):
        config_file_path = os.path.join(directory, self.order.app_paths.config_file_name)
        self.order.save_backup_file(config_file_path)
        vs_config = VsConfigOpener(self.order.os_service, self.order.log,
                                   "PlattformOrdMan.Properties")
        with vs_config.open(config_file_path) as config:
            config.update("DatabaseName", db_name)
            config.update("EnforceAppVersion", "True")
        lab_config_dir = os.path.join(directory, self.order.path_properties.config_lab_subpath)
        create_dirs(self.order.os_service, lab_config_dir, self.order.whatif,
                    self.order.whatif)
        lab_config_file_path = os.path.join(lab_config_dir, self.order.app_paths.config_file_name)
        self.order.os_service.copyfile(config_file_path, lab_config_file_path)
        vs_config = VsConfigOpener(self.order.os_service, self.order.log,
                                   "PlattformOrdMan.Properties")
        with vs_config.open(lab_config_file_path) as config:
            config.update("ApplicationMode", "LAB")

    def _transform_configs(self, directory):
        provider = TransformSettingsProvider(self.order)
        db_name = provider.fetch_env_dependent_variables(directory)
        self._transform_config(directory, db_name)

    def transform_config(self):
        self._transform_configs(self.order.app_paths.production_dir)
        self._transform_configs(self.order.app_paths.validation_dir)


class TransformSettingsProvider:
    def __init__(self, order):
        self.order = order

    def fetch_env_dependent_variables(self, directory):
        if directory == self.order.app_paths.production_dir:
            db_name = "BookKeeping"
        else:
            db_name = "BookKeeping_practice"
        return db_name
