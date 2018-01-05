from __future__ import print_function
from release_ccharp.apps.common.single_file_read_write import ShortcutExaminer


class SqatValidationDeployer:
    def __init__(self, sqat, file_deployer, path_actions):
        self.sqat = sqat
        self.file_deployer = file_deployer
        self.os_service = file_deployer.os_service
        self.shortcut_examiner = ShortcutExaminer(
            self.sqat.branch_provider, self.os_service, self.sqat.windows_commands,
            file_deployer, self.sqat.path_properties.shortcut_path)
        self.path_actions = path_actions

    def run(self):
        self.copy_validation_files()
        self.path_actions.create_shortcut_to_exe()

    def copy_validation_files(self):
        if not self.shortcut_examiner.is_candidate_in_latest:
            self.file_deployer.move_latest_to_archive(self.shortcut_examiner.version_in_latest)
        if self.os_service.exists(self.sqat.path_properties.archive_dir_validation_files):
            self.file_deployer.back_move_from_archive()
        self.file_deployer.copy_to_latest()
