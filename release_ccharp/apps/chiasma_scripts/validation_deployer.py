from __future__ import print_function
import os
from release_ccharp.utils import copytree_preserve_existing


class ChiasmaValidationDeployer:
    def __init__(self, chiasma):
        self.chiasma = chiasma
        self.os_service = chiasma.os_service

    def run(self):
        pass

    def create_shortcut(self):
        shortcut_target = os.path.join(self.chiasma.app_paths.validation_dir, 'Chiasma.exe')
        save_path = os.path.join(self.chiasma.path_properties.user_validations_latest, 'Chiasma.lnk')
        self.chiasma.windows_commands.create_shortcut(save_path, shortcut_target)

    def extract_shortcut_target(self, shortcut_path):
        return self.chiasma.windows_commands.extract_shortcut_target(shortcut_path)

    def copy_validation_files(self):
        source_dir = self.chiasma.path_properties.user_validations_next_dir
        target_dir = self.chiasma.path_properties.latest_validation_files
        copytree_preserve_existing(self.os_service, source_dir, target_dir)

