import os
import re
from snpseq_workflow import *

candidate_subpath = r"candidates"
release_tools_subpath = r"buildconfig\release-tools.config"
confluence_tools_subpath = r"buildconfig\confluence-tools.config"
doc_subpath = r"doc"
doc_metadata_subpath = r"doc\metadata"


class SnpseqPaths:
    def __init__(self, config, repo):
        self.config = config
        self.repo = repo

    @property
    def _repo_root(self):
        return os.path.join(self.config[self.repo]['root_path'], self.repo)

    @property
    def candidate_path(self):
        return os.path.join(self._repo_root, candidate_subpath)

    @property
    def release_tools_config(self):
        return os.path.join(self._repo_root, release_tools_subpath)

    @property
    def confluence_tools_config(self):
        return os.path.join(self._repo_root, confluence_tools_subpath)

    def user_manual_download_path(self, workflow):
        """
        Generates user manual name for coming version, and use the artifact path,
        i.e. the path to the download directory (not the doc path)
        :return: 
        """
        version = str(self._get_current_release_tag(workflow))
        latest_path = self.find_current_release_branch_dir(workflow=workflow)
        manual_base_name = "{}-user-manual".format(self.repo)
        manual_name = "{}-v{}.pdf".format(manual_base_name, version)
        return os.path.join(latest_path, manual_name)

    def find_latest_download_dir(self, workflow):
        """
        Find the download catalog for the latest accepted branch
        :return: The path of latest accepted branch
        """
        current_version = workflow.get_latest_version()
        subdirs = os.listdir(self.candidate_path)
        subdir_path = None
        for subdir in subdirs:
            if re.match('(release|hotfix)-{}'.format(current_version), subdir):
                subdir_path = os.path.join(self.candidate_path, subdir)
        if subdir_path is None:
            raise SnpseqReleaseException("Could not find the download catalog for latest version")
        return subdir_path

    def find_current_release_branch_dir(self, workflow):
        """
        Find the download catalog for the latest candidate branch
        :param workflow: 
        :return: The path of the latest candidate branch
        """
        queue = workflow.get_queue()
        branch = queue[0]
        return os.path.join(self.candidate_path, branch)

    def _get_current_release_tag(self, workflow):
        """
        Get the version of the latest candidate branch
        :param workflow: 
        :return: Version of latest candidate branch
        """
        queue = workflow.get_queue()
        branch = queue[0]
        tag = Conventions.get_tag_from_branch(branch)
        return tag
