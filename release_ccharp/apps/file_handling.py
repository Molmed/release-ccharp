from __future__ import print_function
import os
from abc import abstractmethod
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.utils import copytree_preserve_existing
from release_ccharp.utils import delete_directory_contents


class ValidationDeployer:
    def __init__(self, path_properties, os_service):
        self.path_properties = path_properties
        self.os_service = os_service
        self.path_actions = SnpseqPathActions(
            whatif=False, snpseq_path_properties=self.path_properties,
            os_service=self.os_service)

    def move_to_archive(self, version_in_latest):
        """
        If interrupting an ongoing test for a hotfix, move existing files to archive
        Archive catalog is fetched from shortcut in latest, not the candidate branch
        :return:
        """
        validation_dir = self.path_properties.user_validations_latest
        target_dir = os.path.join(self.path_properties.all_versions, version_in_latest)
        copytree_preserve_existing(self.os_service, validation_dir, target_dir)
        delete_directory_contents(self.os_service, validation_dir)

    def copy_to_latest(self):
        source_dir = self.path_properties.next_validation_files
        target_dir = self.path_properties.latest_validation_files
        copytree_preserve_existing(self.os_service, source_dir, target_dir)

    def back_move_from_archive(self):
        """
        In case of going back to an interrupted validation (for a hotfix during the testperiod)
        :return:
        """
        src = self.path_properties.archive_dir_validation_files
        dst = self.path_properties.latest_validation_files
        copytree_preserve_existing(self.os_service, src, dst)
        delete_directory_contents(self.os_service, src)

    def extract_version_from_path(self, path):
        return self.path_actions.find_version_from_candidate_path(path)


class LatestVersionExaminer:
    @abstractmethod
    def version_in_latest(self):
        pass

    @abstractmethod
    def is_candidate_in_latest(self):
        pass


class ShortcutExaminer(LatestVersionExaminer):
    def __init__(self, branch_provider, os_service, windows_commands,
                 common_deployer, shortcut_path):
        self.branch_provider = branch_provider
        self.os_service = os_service
        self.windows_commands = windows_commands
        self.common_deployer = common_deployer
        self.shortcut_path = shortcut_path

    @property
    def version_in_latest(self):
        shortcut_target = self._extract_shortcut_target(self.shortcut_path)
        return self.common_deployer.extract_version_from_path(shortcut_target)

    def _extract_shortcut_target(self, shortcut_path):
        return self.windows_commands.extract_shortcut_target(shortcut_path)

    @property
    def is_candidate_in_latest(self):
        version_to_validate = self.branch_provider.candidate_version
        if self.os_service.exists(self.shortcut_path):
            return self.version_in_latest == version_to_validate
        else:
            return True
