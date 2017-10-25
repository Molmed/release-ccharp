import unittest
from unittest import skip
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.apps.chiasma import Application
from release_ccharp.apps.common import WindowsCommands
from release_ccharp.utility.os_service import OsService


class ChiasmaValidationDeployTests(unittest.TestCase):
    def setUp(self):
        config = {
            "root_path": r'c:\tmp',
            "git_repo_name": "chiasma",
            "confluence_space_key": "CHI",
            "owner": "GitEdvard"
        }
        branch_provider = FakeBranchProvider()
        wf = SnpseqWorkflow(whatif=False, repo="chiasma")
        wf.config = config
        wf.paths.config = config
        wf.paths.branch_provider = branch_provider
        self.chiasma = Application(wf, branch_provider, OsService(),
                                   WindowsCommands(), whatif=False)

    #@skip("Acts on hard disk. Requires a validation dir and target file Chiasma.exe in validation dir")
    def test_create_shortcut(self):
        self.chiasma.validation_deployer.create_shortcut()

    #@skip("Acts on hard disk. Requires a validation dir, target file Chiasma.exe in validation dir")
    def test_extract_shortcut_target(self):
        shortcut_path = r'c:\tmp\chiasma\uservalidations\latest\chiasma.lnk'
        target = self.chiasma.validation_deployer.extract_shortcut_target(shortcut_path)
        self.assertEqual(r'c:\tmp\chiasma\candidates\new-candidate\validation\chiasma.exe',
                         target.lower())


class FakeBranchProvider:
    def __init__(self):
        self.candidate_version = "1.0.0"
        self.latest_version = "latest-version"
        self.candidate_branch = "new-candidate"