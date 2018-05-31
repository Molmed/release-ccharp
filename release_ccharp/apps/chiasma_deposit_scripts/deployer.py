from __future__ import print_function
from release_ccharp.utils import delete_directory_contents
from release_ccharp.apps.common.base import LogMixin


class ChiasmaDepositDeployer(LogMixin):
    def __init__(self, path_properties, file_deployer, path_actions, branch_provider):
        self.path_properties = path_properties
        self.file_deployer = file_deployer
        self.branch_provider = branch_provider
        self.path_actions = path_actions

    def run(self):
        self.execute_and_log(self.check_source_files_exists)
        self.file_deployer.move_deploy_files()
        self.file_deployer.move_user_manual()
        self.execute_and_log(self.move_to_archive, 'Move validation files and sql script to archive...')

    def check_source_files_exists(self):
        self.file_deployer.check_exe_file_exists()
        self.file_deployer.check_config_file_exists()
        self.file_deployer.check_config_lab_file_exists()
        self.file_deployer.check_user_manual_exists()

    def copy_release_history(self):
        self.file_deployer.copy_release_history()

    def move_to_archive(self):
        """
        Move files to archive folder matching the current candidate
        This method have to be called before the candidate version is accepted.
        :return:
        """
        self.file_deployer.move_latest_to_archive(str(self.branch_provider.candidate_version))
        self.path_actions.create_shortcut_to_exe()
        self.file_deployer.delete_directory_contents(self.path_properties.next_validation_files)
