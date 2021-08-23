from subprocess import call
from shutil import copyfile
import yaml
import os
from release_tools.workflow import Workflow
from release_tools.workflow import Conventions
from release_tools.github import GithubProvider
from release_ccharp.snpseq_paths import SnpseqPathProperties
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.config import Config
from release_ccharp.branches import BranchProvider


class SnpseqWorkflow:
    """
    Initializes a release-tools workflow to act on the github provider
    """
    def __init__(self, whatif, repo, os_service, config=None, branch_provider=None):
        conf = Config()
        self.os_service = os_service
        if config is None:
            self.config = conf.open_config(repo)
        else:
            self.config = config
        self.whatif = whatif
        self.repo = repo
        self.paths = SnpseqPathProperties(self.config, self.repo, os_service, "file_area")
        self.local_paths = SnpseqPathProperties(self.config, self.repo, os_service, "local")
        self.workflow = self._create_workflow()
        self.paths.branch_provider = branch_provider or BranchProvider(self.workflow)
        self.local_paths.branch_provider = branch_provider or BranchProvider(self.workflow)

    def _open_github_provider_config(self, config_file):
        try:
            with self.os_service.open(config_file, 'r') as f:
                contents = yaml.load(f, Loader=yaml.FullLoader)
        except IOError as e:
            msg = 'The config file could not be found. Probably, you can copy the config file from ' \
                  'another adjecent repo to the buildconfig folder. ' \
                  'Original message: {}'.format(str(e))
            raise IOError(msg)
        return contents['access_token'] if contents and "access_token" in contents else None

    def _create_workflow(self):
        owner = self.config['owner']
        githubrepo = self.config['git_repo_name']
        config_file = self.paths.release_tools_config
        whatif = self.whatif
        access_token = self._open_github_provider_config(config_file)
        provider = GithubProvider(owner, githubrepo, access_token)
        return Workflow(provider, Conventions, whatif)

    def create_cand(self, major_inc=False):
        self.workflow.create_release_candidate(major_inc)

    def create_hotfix(self):
        self.workflow.create_hotfix()

    def download(self):
        self.workflow.download_next_in_queue(path=self.local_paths.root_candidates, force=False)

    def accept(self):
        self.workflow.accept_release_candidate(force=False)

    def download_release_history(self):
        """
        Should be called after the candidate is accepted and the release history is 
        updated on GitHub        
        :return: 
        """
        self.workflow.download_release_history(path=self.paths.latest_accepted_release_history)

    def generate_user_manual(self):
        space_key = self.config["confluence_space_key"]
        user_manual = self.paths.user_manual_download_path
        cmd = ["confluence-tools",
                "--config",
                self.paths.confluence_tools_config,
                "space-export",
                space_key,
                user_manual]
        if not self.whatif:
            call(cmd)

    def copy_previous_user_manual(self):
        latest_manual = self.paths.user_manual_path_previous
        next_manual = self.paths.user_manual_download_path
        if not os.path.exists(latest_manual):
            raise SnpseqReleaseException("Previous user manual could not be found: {}".format(latest_manual))
        if not self.whatif:
            copyfile(latest_manual, next_manual)

    def status(self):
        branches = self.workflow.provider.get_branches()
        branch_names = [branch["name"] for branch in branches]

        queue = self.workflow.get_queue()

        latest_version = self.workflow.get_latest_version()
        next_version = self.workflow.get_candidate_version()
        hotfix_version = self.workflow.get_hotfix_version()
        print "Latest version: {}".format(latest_version)
        print "  - Next release version would be: {}".format(next_version)
        print "  - Next hotfix version would be: {}".format(hotfix_version)

        # TODO: Report all release tags too

        print ""
        print "Branches:"
        for branch in branch_names:
            print "  {}{}".format(branch, " *" if (branch in queue) else "")

        print ""
        print "Queue:"
        # TODO: Use cache for api calls when possible
        for branch in queue:
            pull_requests = len(self.workflow.provider.get_pull_requests(branch))
            print "  {} (PRs={})".format(branch, pull_requests)

        # TODO: Compare relevant branches
        print ""

