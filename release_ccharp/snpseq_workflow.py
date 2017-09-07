from release_tools.workflow import Workflow
from release_tools.workflow import Conventions
from release_tools.github import GithubProvider
from subprocess import call
from PyPDF2 import PdfFileWriter
from PyPDF2 import PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import StringIO
import yaml
import os
import re


class SnpseqWorkflow:
    def __init__(self, whatif, repo):
        here = os.path.dirname(__file__)
        path = os.path.join(here, 'release_ccharp.config')
        self.config = None
        with open(path, 'r') as f:
            self.config = yaml.load(f)
        self.whatif = whatif
        self.repo = repo

    def _open_config(self, config_file):
        with open(config_file) as f:
            contents = yaml.load(f)
        return contents['access_token'] if contents and "access_token" in contents else None

    def _create_workflow(self):
        if not self.repo in self.config:
            raise SnpseqReleaseException("This repo name is not present in the config file! '{}'".format(self.repo))
        owner = self.config[self.repo]['owner']
        repo = self.repo
        config_file = self.config[self.repo]['release_tools_config']
        whatif = self.whatif
        access_token = self._open_config(config_file)
        provider = GithubProvider(owner, repo, access_token)
        return Workflow(provider, Conventions, whatif)

    def _find_latest_download_dir(self, parent_path, workflow):
        """
        Find the download catalog for the latest accepted branch
        :param parent_path: Root directory for downloaded archives
        :return: The path of latest accepted branch
        """
        current_version = workflow.get_latest_version()
        subdirs = os.listdir(parent_path)
        subdir_path = None
        for subdir in subdirs:
            if re.match('(release|hotfix)-{}'.format(current_version), subdir):
                subdir_path = os.path.join(parent_path, subdir)
        if subdir_path is None:
            raise SnpseqReleaseException("Could not find the download catalog for latest version")
        return subdir_path

    def create_cand(self, major_inc=False):
        wf = self._create_workflow()
        wf.create_release_candidate(major_inc)

    def create_hotfix(self):
        wf = self._create_workflow()
        wf.create_hotfix()

    def download(self):
        candidate_path = self.config[self.repo]['candidate_path']
        wf = self._create_workflow()
        wf.download_next_in_queue(path=candidate_path, force=False)

    def accept(self):
        wf = self._create_workflow()
        wf.accept_release_candidate(force=False)

    def download_release_history(self):
        candidate_path = self.config[self.repo]['candidate_path']

        wf = self._create_workflow()
        latest_path = self._find_latest_download_dir(parent_path=candidate_path, workflow=wf)
        path = os.path.join(latest_path, "release-history.txt")
        wf.download_release_history(path=path)

    def generate_user_manual(self):
        config = self.config[self.repo]["confluence_tools_config"]
        space_key = self.config[self.repo]["confluence_space_key"]
        candidate_path = self.config[self.repo]['candidate_path']
        manual_base_name = self.config[self.repo]["user_manual_base_name"]
        wf = self._create_workflow()
        version = str(wf.get_latest_version())
        latest_path = self._find_latest_download_dir(parent_path=candidate_path, workflow=wf)
        manual_name = "{}-v{}.pdf".format(manual_base_name, version)
        manual_path = os.path.join(latest_path, manual_name)
        cmd2 = ["confluence-tools", "--config", config, "space-export", space_key, manual_path]
        call(cmd2)


class SnpseqReleaseException(Exception):
    pass
