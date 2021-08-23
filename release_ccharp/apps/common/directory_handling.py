from __future__ import print_function
import os
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.utils import lazyprop
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.utils import copytree_preserve_existing
from release_ccharp.utils import copytree_replace_existing
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
            if pattern.lower() in d.lower():
                return d
        raise SnpseqReleaseException(
            'download directory could not be found under candidate path \n {}'.format(candidate_dir))

    @lazyprop
    def download_dir(self):
        download_directory_name = self.find_download_directory_name()
        return os.path.join(self.path_properties.current_candidate_dir,
                            download_directory_name)

    @lazyprop
    def database_delivery_exe(self):
        return os.path.join(
            self.download_dir,
            r'DatabaseDelivery\bin\Release\DatabaseDelivery.exe'
        )

    @lazyprop
    def validation_dir(self):
        cand_dir = self.path_properties.current_candidate_dir
        return os.path.join(cand_dir, "validation")

    @lazyprop
    def production_dir(self):
        cand_dir = self.path_properties.current_candidate_dir
        return os.path.join(cand_dir, "production")

    @lazyprop
    def production_config_lab_dir(self):
        return os.path.join(self.production_dir, self.path_properties.config_lab_subpath)

    @lazyprop
    def config_file_name(self):
        return "{}.exe.config".format(self.config["exe_file_name_base"])

    def common_move_candidates(self, project_root_directory):
        bin_dir = os.path.join(project_root_directory, 'bin')
        release_dir = os.path.join(bin_dir, 'release')
        self.os_service.copytree(release_dir, self.validation_dir)
        self.os_service.copytree(release_dir, self.production_dir)

    @lazyprop
    def common_assembly_file_path(self):
        properties = os.path.join(self.config["project_root_dir"], 'properties')
        assembly_subpath = os.path.join(properties, 'assemblyinfo.cs')
        assembly_file_path = os.path.join(
            self.download_dir, assembly_subpath)
        if not self.os_service.exists(assembly_file_path):
            raise SnpseqReleaseException(
                "The assembly info file could not be found {}".format(assembly_file_path))
        return assembly_file_path


class FileDeployer:
    def __init__(self, path_properties, os_service, config, app_paths):
        self.path_properties = path_properties
        self.os_service = os_service
        self.config = config
        self.app_paths = app_paths
        self.path_actions = SnpseqPathActions(
            whatif=False, path_properties=self.path_properties,
            os_service=self.os_service)

    def move_latest_to_archive(self, version):
        validation_dir = self.path_properties.user_validations_latest
        target_dir = os.path.join(self.path_properties.all_versions, version)
        copytree_preserve_existing(self.os_service, validation_dir, target_dir)
        delete_directory_contents(self.os_service, validation_dir)

    def move_sql_scripts_to_archive(self, version):
        src = self.path_properties.next_sql_updates
        dst = self.path_properties.archive_sql_updates
        copytree_preserve_existing(self.os_service, src, dst)
        delete_directory_contents(self.os_service, src)

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

    def check_exe_file_exists(self):
        exe_filename = '{}.exe'.format(self.config['exe_file_name_base'])
        exe = os.path.join(self.app_paths.production_dir, exe_filename)
        if not self.os_service.exists(exe):
            raise FileDoesNotExistsException(exe)

    def check_file_in_production_exists(self, file_name):
        file_path = os.path.join(self.app_paths.production_dir, file_name)
        if not self.os_service.exists(file_path):
            raise FileDoesNotExistsException(file_path)

    def check_config_file_exists(self):
        config = os.path.join(self.app_paths.production_dir, self.app_paths.config_file_name)
        if not self.os_service.exists(config):
            raise FileDoesNotExistsException(config)

    def check_production_file_exists(self, filename):
        path = os.path.join(self.app_paths.production_dir, filename)
        if not self.os_service.exists(path):
            raise FileDoesNotExistsException(path)

    def check_config_lab_file_exists(self):
        config_lab = os.path.join(
            self.app_paths.production_config_lab_dir, self.app_paths.config_file_name)
        if not self.os_service.exists(config_lab):
            raise FileDoesNotExistsException(config_lab)

    def check_user_manual_exists(self):
        user_manual = self.path_properties.user_manual_download_path
        if not self.os_service.exists(user_manual):
            raise FileDoesNotExistsException(user_manual)

    def move_deploy_files(self):
        print('Copy files to deploy catalog...')
        src = self.app_paths.production_dir
        dst = self.app_paths.config['deploy_root_path']
        copytree_replace_existing(self.os_service, src, dst)
        print('ok')

    def move_user_manual(self):
        print('Copy user manual to doc catalog...')
        src = self.path_properties.user_manual_download_path
        dst = os.path.join(self.path_properties.doc, self.path_properties.user_manual_name)
        self.os_service.copyfile(src, dst)
        print('ok')

    def copy_release_history(self):
        print('Copy release history to doc catalog...')
        src_release_history = self.path_properties.latest_accepted_release_history
        release_history_base_name = os.path.basename(src_release_history)
        dst = os.path.join(self.path_properties.doc, release_history_base_name)
        self.os_service.copyfile(src_release_history, dst)
        print('ok')

    def copy_file(self, filename, src_dir, dst_dir):
        src = os.path.join(src_dir, filename)
        dst = os.path.join(dst_dir, filename)
        self.os_service.copyfile(src, dst)

    def check_not_already_run(self):
        if self.os_service.exists(self.app_paths.production_dir) or \
                self.os_service.exists(self.app_paths.validation_dir):
            raise SnpseqReleaseException(
                ("Production or validation catalog already exists. " 
                "They need to be removed before continuing"))

    def delete_directory_contents(self, target_dir):
        delete_directory_contents(self.os_service, target_dir)


class FileDoesNotExistsException(Exception):
    pass
