from __future__ import print_function
from release_ccharp.apps.common.single_file_read_write import ShortcutExaminer


class OrderValidationDeployer:
    def __init__(self, order, file_deployer, path_actions):
        self.order = order
        self.file_deployer = file_deployer
        self.os_service = file_deployer.os_service
        self.shortcut_examiner = ShortcutExaminer(
            self.order.branch_provider, self.os_service, self.order.windows_commands,
            file_deployer, self.order.path_properties.shortcut_path)
        self.path_actions = path_actions

    def run(self):
        self.copy_validation_files()
        self.path_actions.create_shortcut_to_exe()

    def copy_validation_files(self):
        if not self.shortcut_examiner.is_candidate_in_latest:
            self.file_deployer.move_latest_to_archive(self.shortcut_examiner.version_in_latest)
        if self.os_service.exists(self.order.path_properties.archive_dir_validation_files):
            self.file_deployer.back_move_from_archive()
        self.file_deployer.copy_to_latest()
