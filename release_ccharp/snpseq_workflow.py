from release_tools.workflow import Workflow
from release_tools.workflow import Conventions
from release_tools.github import GithubProvider
from release_ccharp.snpseq_paths import *
from release_ccharp.exceptions import SnpseqReleaseException
from subprocess import call
from PyPDF2 import PdfFileWriter
from PyPDF2 import PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from shutil import copyfile
import StringIO
import yaml
import os


class SnpseqWorkflow:
    def __init__(self, whatif, repo):
        here = os.path.dirname(__file__)
        path = os.path.join(here, 'release_ccharp.config')
        self.config = None
        with open(path, 'r') as f:
            self.config = yaml.load(f)
        self.whatif = whatif
        self.repo = repo
        self.paths = SnpseqPaths(self.config, self.repo)

    def _open_config(self, config_file):
        with open(config_file) as f:
            contents = yaml.load(f)
        return contents['access_token'] if contents and "access_token" in contents else None

    def _create_workflow(self):
        if not self.repo in self.config:
            raise SnpseqReleaseException("This repo name is not present in the config file! '{}'".format(self.repo))
        owner = self.config[self.repo]['owner']
        repo = self.repo
        config_file = self.paths.release_tools_config
        whatif = self.whatif
        access_token = self._open_config(config_file)
        provider = GithubProvider(owner, repo, access_token)
        return Workflow(provider, Conventions, whatif)

    def create_cand(self, major_inc=False):
        wf = self._create_workflow()
        wf.create_release_candidate(major_inc)

    def create_hotfix(self):
        wf = self._create_workflow()
        wf.create_hotfix()

    def download(self):
        wf = self._create_workflow()
        wf.download_next_in_queue(path=self.paths.candidate_path, force=False)

    def accept(self):
        wf = self._create_workflow()
        wf.accept_release_candidate(force=False)

    def download_release_history(self):
        wf = self._create_workflow()
        latest_path = self.paths.find_previous_download_dir(workflow=wf)
        path = os.path.join(latest_path, "release-history.txt")
        wf.download_release_history(path=path)

    def generate_user_manual(self):
        space_key = self.config[self.repo]["confluence_space_key"]
        wf = self._create_workflow()
        user_manual = self.paths.user_manual_download_path(workflow=wf)
        cmd = ["confluence-tools",
                "--config",
                self.paths.confluence_tools_config,
                "space-export",
                space_key,
                user_manual]
        if not self.whatif:
            call(cmd)

    def copy_previous_user_manual(self):
        workflow = self._create_workflow()
        latest_manual = self.paths.user_manual_path_previous(workflow)
        next_manual = self.paths.user_manual_download_path(workflow)
        if not os.path.exists(latest_manual):
            raise SnpseqReleaseException("Previous user manual could not be found: {}".format(latest_manual))
        if not self.whatif:
            copyfile(latest_manual, next_manual)
