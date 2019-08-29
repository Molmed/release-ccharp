import unittest
import os
import pyperclip
from pyfakefs import fake_filesystem
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.snpseq_paths import SnpseqPathProperties
from release_ccharp.utils import create_dirs
from tests.unit.utility.fake_os_service import FakeOsService


class BaseTests(unittest.TestCase):
    def base_setup(self, config, repo):
        branch_provider = FakeBranchProvider()
        self.filesystem = fake_filesystem.FakeFilesystem()
        os_service = FakeOsService(self.filesystem)
        self.os_module = os_service.os_module
        path_properties = SnpseqPathProperties(config, repo, os_service)
        path_properties.branch_provider = branch_provider
        self.prepare_folder_tree(os_service, branch_provider, path_properties, self.filesystem)
        wf = SnpseqWorkflow(whatif=False, repo=repo, os_service=os_service, config=config)
        wf.paths.branch_provider = branch_provider
        return wf, branch_provider, os_service

    def prepare_folder_tree(self, os_service, branch_provider, path_properties, filesystem):
        path_actions = SnpseqPathActions(
            whatif=False, path_properties=path_properties,
            os_service=os_service
        )
        path_actions.generate_folder_tree()
        create_dirs(os_service, path_properties.current_candidate_dir, False, False)
        latest_candidate = 'release-{}'.format(branch_provider.latest_version)
        latest_dir = os.path.join(path_properties.root_candidates, latest_candidate)
        create_dirs(os_service, latest_dir, False, False)
        filesystem.create_file(path_properties.release_tools_config, contents='none')

    def copy_to_clipboard(self, var):
        if isinstance(var, set):
            var = list(var)
        if isinstance(var, list):
            var = '\n\n'.join(var)
        print('copied to clipboard:\n{}'.format(var))
        pyperclip.copy('{}'.format(var))


class FakeBranchProvider:
    def __init__(self):
        self.candidate_version = "1.0.0"
        self.latest_version = "0.0.9"
        self.candidate_branch = "release-1.0.0"
