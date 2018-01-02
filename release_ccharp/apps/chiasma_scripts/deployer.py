from __future__ import print_function
from release_ccharp.utils import copytree_replace_existing


class ChiasmaDeployer:
    def __init__(self, path_properties, common_deployer):
        self.path_properties = path_properties
        self.common_deployer = common_deployer

    def run(self):
        self.check_source_files_exists()
        self.common_deployer.move_deploy_files()

    def check_source_files_exists(self):
        print('Check that source files exists ...')

        self.common_deployer.check_exe_file_exists()
        self.common_deployer.check_config_file_exists()
        self.common_deployer.check_config_lab_file_exists()
        self.common_deployer.check_user_manual_exists()

        print('ok')
