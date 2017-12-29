from __future__ import print_function
import os
from release_ccharp.utils import lazyprop
from release_ccharp.apps.common.single_file_read_write import ShortcutExaminer


class ChiasmaValidationDeployer:
    def __init__(self, chiasma, common_deployer):
        self.chiasma = chiasma
        self.common_deployer = common_deployer
        self.os_service = common_deployer.os_service
        self.shortcut_examiner = ShortcutExaminer(
            self.chiasma.branch_provider, self.os_service, self.chiasma.windows_commands,
            common_deployer, self.shortcut_path
        )

    def run(self):
        self.copy_validation_files()
        self.create_shortcut()

    @lazyprop
    def shortcut_path(self):
        filename = '{}.lnk'.format(self.chiasma.config['exe_file_name_base'])
        return os.path.join(self.chiasma.path_properties.user_validations_latest, filename)

    def create_shortcut(self):
        exe_filename = '{}.exe'.format(self.chiasma.config['exe_file_name_base'])
        shortcut_target = os.path.join(self.chiasma.app_paths.validation_dir, exe_filename)
        self.chiasma.windows_commands.create_shortcut(self.shortcut_path, shortcut_target)

    def copy_validation_files(self):
        if not self.shortcut_examiner.is_candidate_in_latest:
            self.common_deployer.move_to_archive(self.shortcut_examiner.version_in_latest)
        if self.os_service.exists(self.chiasma.path_properties.archive_dir_validation_files):
            self.common_deployer.back_move_from_archive()
        self.common_deployer.copy_to_latest()
