from __future__ import print_function
from release_ccharp.utils import copytree_replace_existing


class ChiasmaDeployer:
    def __init__(self, path_properties, file_deployer):
        self.path_properties = path_properties
        self.file_deployer = file_deployer

    def run(self):
        self.check_source_files_exists()
        self.file_deployer.move_deploy_files()
        self.file_deployer.move_user_manual()

    def check_source_files_exists(self):
        print('Check that source files exists ...')

        self.file_deployer.check_exe_file_exists()
        self.file_deployer.check_config_file_exists()
        self.file_deployer.check_config_lab_file_exists()
        self.file_deployer.check_user_manual_exists()

        print('ok')

    def copy_release_history(self):
        self.file_deployer.copy_release_history()
