import os
import re
import yaml
from release_ccharp.exceptions import SnpseqReleaseException
from release_tools.workflow import Conventions
from release_ccharp.utils import create_dirs
from release_ccharp.utils import lazyprop


class SnpseqPathProperties:
    def __init__(self, config, repo, os_service):
        self.config = config
        self.repo = repo
        self.os_service = os_service
        self.branch_provider = None
        sub_paths = self._load_subpaths()
        self.build_config_subpath = sub_paths['build_config_subpath']
        self.release_tools_subpath = sub_paths['release_tools_subpath']
        self.confluence_tools_subpath = sub_paths['confluence_tools_subpath']
        self.candidate_subpath = sub_paths['candidate_subpath']
        self.config_lab_subpath = sub_paths['config_lab_subpath']
        self.devel_environment_subpath = sub_paths['devel_environment_subpath']
        self.doc_subpath = sub_paths['doc_subpath']
        self.doc_metadata_subpath = sub_paths['doc_metadata_subpath']
        self.user_validations_subpath = sub_paths['user_validations_subpath']
        self.user_validations_all_version_subpath = sub_paths['user_validations_all_version_subpath']
        self.user_validations_next_hotfix_subpath = sub_paths ['user_validations_next_hotfix_subpath']
        self.user_validations_next_release_subpath = sub_paths['user_validations_next_release_subpath']
        self.user_validations_validation_files_subpath = sub_paths['user_validations_validation_files_subpath']
        self.user_validations_sql_updates_subpath = sub_paths['user_validations_sql_updates_subpath']
        self.user_validations_latest_subpath = sub_paths['user_validations_latest_subpath']

    def _load_subpaths(self):
        here = os.path.dirname(__file__)
        path = os.path.join(here, 'paths.config')
        with open(path, 'r') as f:
            sub_paths = yaml.load(f)
        return sub_paths

    @property
    def _repo_root(self):
        return os.path.join(self.config['root_path'], self.repo)

    @property
    def _candidate_tag(self):
        """
        Get the version of the latest candidate branch
        :param workflow: 
        :return: Version of latest candidate branch
        """
        tag = Conventions.get_tag_from_branch(self.branch_provider.candidate_branch)
        return tag

    @property
    def root_candidates(self):
        return os.path.join(self._repo_root, self.candidate_subpath)

    @property
    def release_tools_config(self):
        return os.path.join(self._repo_root, self.release_tools_subpath)

    @property
    def confluence_tools_config(self):
        return os.path.join(self._repo_root, self.confluence_tools_subpath)

    @property
    def user_manual_download_path(self):
        """
        Generates user manual name for coming version, and use the artifact path,
        i.e. the path to the download directory (not the doc path)
        :return: 
        """
        latest_path = self.current_candidate_dir
        return os.path.join(latest_path, self.user_manual_name)

    @property
    def user_manual_name(self):
        version = str(self._candidate_tag)
        manual_base_name = "{}-user-manual".format(self.repo)
        return "{}-{}.pdf".format(manual_base_name, version)

    @property
    def user_manual_path_previous(self):
        manual_base_name = "{}-user-manual".format(self.repo)
        manual_name = "{}-v{}.pdf".format(manual_base_name, self.branch_provider.latest_version)
        latest_path = self.latest_accepted_candidate_dir
        return os.path.join(latest_path, manual_name)

    @property
    def latest_accepted_candidate_dir(self):
        """
        Find the download catalog for the latest accepted branch
        :return: The path of latest accepted branch
        """
        subdirs = self.os_service.listdir(self.root_candidates)
        subdir_path = None
        for subdir in subdirs:
            if re.match('(release|hotfix)-{}'.format(self.branch_provider.latest_version), subdir):
                subdir_path = os.path.join(self.root_candidates, subdir)
        if subdir_path is None:
            raise SnpseqReleaseException("Could not find the download catalog for latest version")
        return subdir_path

    @property
    def latest_accepted_release_history(self):
        latest_path = self.latest_accepted_candidate_dir
        return os.path.join(latest_path, "release-history.txt")

    @property
    def current_candidate_dir(self):
        """
        Find the download catalog for the latest candidate branch
        :return: The path of the latest candidate branch
        """
        return os.path.join(self.root_candidates, self.branch_provider.candidate_branch)

    @property
    def _user_validations(self):
        return os.path.join(self._repo_root, self.user_validations_subpath)

    @property
    def all_versions(self):
        return os.path.join(self._user_validations, self.user_validations_all_version_subpath)

    @property
    def user_validations_latest(self):
        return os.path.join(self._user_validations, self.user_validations_latest_subpath)

    @property
    def user_validations_next_release(self):
        return os.path.join(self.all_versions, self.user_validations_next_release_subpath)

    @property
    def user_validations_next_hotfix(self):
        return os.path.join(self.all_versions, self.user_validations_next_hotfix_subpath)

    @property
    def user_validations_next_dir(self):
        if "release" in self.branch_provider.candidate_branch:
            return self.user_validations_next_release
        else:
            return self.user_validations_next_hotfix

    @property
    def next_validation_files(self):
        """
        Directory name always 'ValidationFiles', and may be located either in
        _next_release or _next_hotfix
        :return:
        """
        return os.path.join(self.user_validations_next_dir, self.user_validations_validation_files_subpath)

    @property
    def next_sql_updates(self):
        """
        Directory name always 'SQLUpdates', and may be located either in
        _next_release or _next_hotfix
        :return:
        """
        return os.path.join(self.user_validations_next_dir, self.user_validations_sql_updates_subpath)

    @property
    def archive_sql_updates(self):
        """
        Archive matching the current candidate
        ...\AllVersions\<candidate version>\SQLUpdates
        :return:
        """
        archive_version_dir = os.path.join(self.all_versions, str(self.branch_provider.candidate_version))
        return os.path.join(archive_version_dir, self.user_validations_sql_updates_subpath)

    @property
    def latest_validation_files(self):
        return os.path.join(self.user_validations_latest, self.user_validations_validation_files_subpath)

    @property
    def archive_dir_validation_files(self):
        archive_version_dir = os.path.join(self.all_versions, str(self.branch_provider.candidate_version))
        return os.path.join(archive_version_dir, self.user_validations_validation_files_subpath)

    @property
    def doc(self):
        return os.path.join(self._repo_root, self.doc_subpath)

    @lazyprop
    def shortcut_path(self):
        filename = '{}.lnk'.format(self.config['exe_file_name_base'])
        return os.path.join(self.user_validations_latest, filename)


class SnpseqPathActions:
    def __init__(self, whatif, path_properties, os_service, app_paths=None, windows_commands=None):
        self.path_properties = path_properties
        self.whatif = whatif
        self.os_service = os_service
        self.app_paths = app_paths
        self.windows_commands = windows_commands

    def generate_folder_tree(self):
        root_path = self.path_properties._repo_root
        # Generate path variables
        build_config = os.path.join(root_path, self.path_properties.build_config_subpath)
        candidates = os.path.join(root_path, self.path_properties.candidate_subpath)
        devel_environment = os.path.join(root_path, self.path_properties.devel_environment_subpath)
        doc = os.path.join(root_path, self.path_properties.doc_subpath)
        doc_metadata = os.path.join(doc, self.path_properties.doc_metadata_subpath)
        user_validations = os.path.join(root_path, self.path_properties.user_validations_subpath)
        user_validations_latest = os.path.join(user_validations, self.path_properties.user_validations_latest_subpath)
        latest_validation_files = os.path.join(user_validations_latest, self.path_properties.user_validations_validation_files_subpath)
        all_versions = os.path.join(user_validations, self.path_properties.user_validations_all_version_subpath)
        next_hotfix = os.path.join(all_versions, self.path_properties.user_validations_next_hotfix_subpath)
        next_release = os.path.join(all_versions, self.path_properties.user_validations_next_release_subpath)
        validation_files_next_hotfix = os.path.join(next_hotfix, self.path_properties.user_validations_validation_files_subpath)
        sql_updates_next_hotfix = os.path.join(next_hotfix, self.path_properties.user_validations_sql_updates_subpath)
        validation_files_next_release = os.path.join(next_release, self.path_properties.user_validations_validation_files_subpath)
        sql_updates_next_release = os.path.join(next_release, self.path_properties.user_validations_sql_updates_subpath)
        # Create paths
        self.create_dirs(build_config)
        self.create_dirs(candidates)
        self.create_dirs(devel_environment)
        self.create_dirs(doc)
        self.create_dirs(doc_metadata)
        self.create_dirs(user_validations)
        self.create_dirs(user_validations_latest)
        self.create_dirs(latest_validation_files)
        self.create_dirs(all_versions)
        self.create_dirs(next_hotfix)
        self.create_dirs(next_release)
        self.create_dirs(validation_files_next_hotfix)
        self.create_dirs(sql_updates_next_hotfix)
        self.create_dirs(validation_files_next_release)
        self.create_dirs(sql_updates_next_release)
        self.create_dirs(self.path_properties.config['deploy_root_path'])

    def create_dirs(self, path):
        create_dirs(self.os_service, path, self.whatif, self.whatif)

    def find_version_from_candidate_path(self, candidate_path):
        res = re.match(r'.*(release|hotfix)-(\d+)\.(\d+)\.(\d+).*', candidate_path)
        version = '{}.{}.{}'.format(res.group(2), res.group(3), res.group(4))
        return version

    def create_shortcut_to_exe(self):
        exe_filename = '{}.exe'.format(self.path_properties.config['exe_file_name_base'])
        shortcut_target = os.path.join(self.app_paths.validation_dir, exe_filename)
        self.windows_commands.create_shortcut(
            self.path_properties.shortcut_path, shortcut_target)

