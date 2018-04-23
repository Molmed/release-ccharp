from __future__ import print_function
import os
from release_ccharp.utils import lazyprop
from release_ccharp.apps.common.single_file_read_write import ShortcutExaminer


class FPValidationDeployer:
    def __init__(self, fp, file_deployer, path_actions, os_service,
                 branch_provider, windows_commands, path_properties):
        self.fp = fp
        self.file_deployer = file_deployer
        self.os_service = os_service
        self.path_properties = path_properties
        self.shortcut_examiner = ShortcutExaminer(
            branch_provider, self.os_service, windows_commands,
            file_deployer, self.path_properties.shortcut_path)
        self.path_actions = path_actions

    def run(self):
        self.copy_validation_files()
        self.copy_config_file()
        self.path_actions.create_shortcut_to_exe()

    def copy_validation_files(self):
        if not self.shortcut_examiner.is_candidate_in_latest:
            self.file_deployer.move_latest_to_archive(self.shortcut_examiner.version_in_latest)
        if self.os_service.exists(self.path_properties.archive_dir_validation_files):
            self.file_deployer.back_move_from_archive()
        self.file_deployer.copy_to_latest()

    def copy_config_file(self):
        src = os.path.join(self.file_deployer.app_paths.validation_dir, 'FPDatabaseConfig.txt')
        dst = os.path.join(self.path_properties.user_validations_latest, 'FPDatabaseConfig.txt')
        self.os_service.copyfile(src, dst)

