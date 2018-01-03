import unittest
import os
from pyfakefs import fake_filesystem
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.apps.chiasma import Application
from release_ccharp.utils import create_dirs
from tests.unit.utility.fake_os_service import FakeOsService
from tests.unit.utility.fake_windows_commands import FakeWindowsCommands


class ChiasmaBaseTests(unittest.TestCase):
    def base_setup(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "chiasma",
            "exe_file_name_base": "Chiasma",
            "project_root_dir" : "Chiasma",
            "owner": "GitEdvard",
            "deploy_root_path": r'c:\xxx\deploy'
        }
        branch_provider = FakeBranchProvider()
        self.filesystem = fake_filesystem.FakeFilesystem()
        os_service = FakeOsService(self.filesystem)
        self.os_module = os_service.os_module
        wf = SnpseqWorkflow(whatif=False, repo="chiasma", os_service=os_service)
        wf.config = config
        wf.paths.config = config
        wf.paths.branch_provider = branch_provider
        self.chiasma = Application(wf, branch_provider, os_service,
                                   FakeWindowsCommands(self.filesystem), whatif=False)

        path_actions = SnpseqPathActions(
            whatif=False, path_properties=self.chiasma.path_properties,
            os_service=os_service
        )
        path_actions.generate_folder_tree()
        create_dirs(os_service, self.chiasma.path_properties.current_candidate_dir, False, False)
        latest_candidate = 'release-{}'.format(branch_provider.latest_version)
        latest_dir = os.path.join(self.chiasma.path_properties.root_candidates, latest_candidate)
        create_dirs(os_service, latest_dir, False, False)


class FakeBranchProvider:
    def __init__(self):
        self.candidate_version = "1.0.0"
        self.latest_version = "0.0.9"
        self.candidate_branch = "release-1.0.0"
