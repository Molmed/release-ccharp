from __future__ import print_function
from release_ccharp.utils import delete_directory_contents


class ChiasmaDeployer:
    def __init__(self, path_properties, file_deployer, path_actions, os_service, branch_provider):
        self.path_properties = path_properties
        self.file_deployer = file_deployer
        self.branch_provider = branch_provider
        self.path_actions = path_actions
        self.os_service = os_service

    def run(self):
        self.check_source_files_exists()
        self.file_deployer.move_deploy_files()
        self.file_deployer.move_user_manual()
        self.move_to_archive()

    def check_source_files_exists(self):
        print('Check that source files exists ...')

        self.file_deployer.check_exe_file_exists()
        self.file_deployer.check_config_file_exists()
        self.file_deployer.check_config_lab_file_exists()
        self.file_deployer.check_user_manual_exists()

        print('ok')

    def copy_release_history(self):
        self.file_deployer.copy_release_history()

    def move_to_archive(self):
        """
        Move files to archive folder matching the current candidate
        This method have to be called before the candidate version is accepted.
        :return:
        """
        print('Move validation files and sql script to archive...')
        self.file_deployer.move_latest_to_archive(str(self.branch_provider.candidate_version))
        self.file_deployer.move_sql_scripts_to_archive(str(self.branch_provider.candidate_version))
        self.path_actions.create_shortcut_to_exe()
        delete_directory_contents(self.os_service, self.path_properties.next_validation_files)
        print('ok')
