from __future__ import print_function
import os
from release_ccharp.utils import lazyprop
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.utils import copytree_preserve_existing
from release_ccharp.utils import delete_directory_contents


class AppPaths:
    """
    Handles directories which is located under a specific candidate (properties and path actions).
    This directory structure may differ between applications, and some
    properties and methods may therefore only be applicable to some of the apps.
    """
    def __init__(self, config, path_properties, os_service):
        self.config = config
        self.path_properties = path_properties
        self.os_service = os_service

    def find_download_directory_name(self):
        candidate_dir = self.path_properties.current_candidate_dir
        pattern = "{}-{}".format(self.config["owner"], self.config["git_repo_name"])
        oss = self.os_service
        dir_lst = [o for o in oss.listdir(candidate_dir) if oss.isdir(os.path.join(candidate_dir, o))]
        for d in dir_lst:
            if pattern in d:
                return d
        return None

    @lazyprop
    def download_dir(self):
        return os.path.join(self.path_properties.current_candidate_dir,
                            self.find_download_directory_name())

    @lazyprop
    def validation_dir(self):
        cand_dir = self.path_properties.current_candidate_dir
        return os.path.join(cand_dir, "validation")

    @lazyprop
    def production_dir(self):
        cand_dir = self.path_properties.current_candidate_dir
        return os.path.join(cand_dir, "production")

    @lazyprop
    def config_file_name(self):
        return "{}.exe.config".format(self.config["git_repo_name"])

    def move_candidates(self):
        release_subdir = os.path.join(self.config["git_repo_name"], r'bin\release')
        release_dir = os.path.join(self.download_dir, release_subdir)
        self.os_service.copytree(release_dir, self.validation_dir)
        self.os_service.copytree(release_dir, self.production_dir)


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
