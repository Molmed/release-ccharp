from __future__ import print_function
import os
from release_ccharp.utils import copytree_preserve_existing
from release_ccharp.utils import delete_directory_contents
from release_ccharp.utils import lazyprop
from release_ccharp.snpseq_paths import SnpseqPathActions


class ChiasmaValidationDeployer:
    def __init__(self, chiasma):
        self.chiasma = chiasma
        self.os_service = chiasma.os_service
        self.path_actions = SnpseqPathActions(
            whatif=False, snpseq_path_properties=self.chiasma.path_properties,
            os_service=self.os_service)

    def run(self):
        self.copy_validation_files()
        self.create_shortcut()

    @lazyprop
    def shortcut_path(self):
        return os.path.join(self.chiasma.path_properties.user_validations_latest, 'Chiasma.lnk')

    def create_shortcut(self):
        shortcut_target = os.path.join(self.chiasma.app_paths.validation_dir, 'Chiasma.exe')
        self.chiasma.windows_commands.create_shortcut(self.shortcut_path, shortcut_target)

    def extract_shortcut_target(self, shortcut_path):
        return self.chiasma.windows_commands.extract_shortcut_target(shortcut_path)

    def _move_to_archive(self):
        """
        If interupting an ongoing test for a hotfix, move existing files to archive
        Archive catalog is fetched from shortcut in latest, not the candidate branch
        :return:
        """
        validation_dir = self.chiasma.path_properties.user_validations_latest
        target_dir = os.path.join(self.chiasma.path_properties.all_versions, self._version_from_shortcut)
        copytree_preserve_existing(self.os_service, validation_dir, target_dir)
        delete_directory_contents(self.os_service, validation_dir)

    def _back_move_from_archive(self):
        """
        In case of going back to an interrupted validation (for a hotfix during the testperiod)
        :return:
        """
        src = self.chiasma.path_properties.validation_archive_dir
        dst = self.chiasma.path_properties.latest_validation_files
        copytree_preserve_existing(self.os_service, src, dst)
        delete_directory_contents(self.os_service, src)


    def _copy_to_latest(self):
        source_dir = self.chiasma.path_properties.next_validation_files
        target_dir = self.chiasma.path_properties.latest_validation_files
        copytree_preserve_existing(self.os_service, source_dir, target_dir)

    @property
    def _version_from_shortcut(self):
        shortcut_target = self.extract_shortcut_target(self.shortcut_path)
        return self._extract_version_from_path(shortcut_target)

    @property
    def _is_candidate_in_latest(self):
        version_to_validate = self.chiasma.branch_provider.candidate_version
        if self.os_service.exists(self.shortcut_path):
            return self._version_from_shortcut == version_to_validate
        else:
            return True

    def _extract_version_from_path(self, path):
        return self.path_actions.find_version_from_candidate_path(path)

    def copy_validation_files(self):
        if not self._is_candidate_in_latest:
            self._move_to_archive()
        if self.os_service.exists(self.chiasma.path_properties.validation_archive_dir):
            self._back_move_from_archive()
        self._copy_to_latest()
