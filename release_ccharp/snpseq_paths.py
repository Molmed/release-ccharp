import os
import re
import yaml
from release_ccharp.exceptions import SnpseqReleaseException
from release_tools.workflow import Conventions


class SnpseqPathProperties:
    def __init__(self, config, repo):
        self.config = config
        self.repo = repo
        self.branch_provider = None
        sub_paths = self._load_subpaths()
        self.build_config_subpath = sub_paths['build_config_subpath']
        self.release_tools_subpath = sub_paths['release_tools_subpath']
        self.confluence_tools_subpath = sub_paths['confluence_tools_subpath']
        self.candidate_subpath = sub_paths['candidate_subpath']
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
    def candidate_root_path(self):
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
        version = str(self._candidate_tag)
        latest_path = self.current_candidate_dir
        manual_base_name = "{}-user-manual".format(self.repo)
        manual_name = "{}-{}.pdf".format(manual_base_name, version)
        return os.path.join(latest_path, manual_name)

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
        subdirs = os.listdir(self.candidate_root_path)
        subdir_path = None
        for subdir in subdirs:
            if re.match('(release|hotfix)-{}'.format(self.branch_provider.latest_version), subdir):
                subdir_path = os.path.join(self.candidate_root_path, subdir)
        if subdir_path is None:
            raise SnpseqReleaseException("Could not find the download catalog for latest version")
        return subdir_path

    @property
    def current_candidate_dir(self):
        """
        Find the download catalog for the latest candidate branch
        :param workflow: 
        :return: The path of the latest candidate branch
        """
        return os.path.join(self.candidate_root_path, self.branch_provider.candidate_branch)


class SnpseqPathActions:
    def __init__(self, whatif, snpseq_path_properties):
        self.snpseq_path_properties = snpseq_path_properties
        self.whatif = whatif

    def generate_folder_tree(self):
        root_path = self.snpseq_path_properties._repo_root
        # Generate path variables
        build_config = os.path.join(root_path, self.snpseq_path_properties.build_config_subpath)
        candidates = os.path.join(root_path, self.snpseq_path_properties.candidate_subpath)
        devel_environment = os.path.join(root_path, self.snpseq_path_properties.devel_environment_subpath)
        doc = os.path.join(root_path, self.snpseq_path_properties.doc_subpath)
        doc_metadata = os.path.join(doc, self.snpseq_path_properties.doc_metadata_subpath)
        user_validations = os.path.join(root_path, self.snpseq_path_properties.user_validations_subpath)
        user_validations_latest = os.path.join(user_validations, self.snpseq_path_properties.user_validations_latest_subpath)
        latest_validation_files = os.path.join(user_validations_latest, self.snpseq_path_properties.user_validations_subpath)
        all_versions = os.path.join(user_validations, self.snpseq_path_properties.user_validations_all_version_subpath)
        next_hotfix = os.path.join(all_versions, self.snpseq_path_properties.user_validations_next_hotfix_subpath)
        next_release = os.path.join(all_versions, self.snpseq_path_properties.user_validations_next_release_subpath)
        validation_files_next_hotfix = os.path.join(next_hotfix, self.snpseq_path_properties.user_validations_validation_files_subpath)
        sql_updates_next_hotfix = os.path.join(next_hotfix, self.snpseq_path_properties.user_validations_sql_updates_subpath)
        validation_files_next_release = os.path.join(next_release, self.snpseq_path_properties.user_validations_validation_files_subpath)
        sql_updates_next_release = os.path.join(next_release, self.snpseq_path_properties.user_validations_sql_updates_subpath)
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

    def create_dirs(self, path):
        if not os.path.exists(path):
            print("Create directory: {}".format(path))
            if not self.whatif:
                os.makedirs(path)
        else:
            print "Path already exists: {}".format(path)
