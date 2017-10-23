from __future__ import print_function
import unittest
from release_ccharp.apps.chiasma import Application
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.apps.dev_environment import TestEnvironmentProvider


class ChiasmaBuildTests(unittest.TestCase):
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
        self.chiasma = Application(wf, branch_provider, whatif=False)

    def test__get_version(self):
        version = self.chiasma.branch_provider.candidate_version
        self.assertEqual("1.0.0", version)

    def test__repo_root(self):
        root_path = self.chiasma.path_properties._repo_root
        self.assertEqual(r'c:\tmp\chiasma', root_path)

    def test_replace_assebly_version(self):
        s = """line1
[assembly: AssemblyVersion("1.6.*")]
line 3"""
        (current, new) = self.chiasma.binary_version_updater.get_assembly_replace_strings(s, "1.0.0")
        self.assertEqual("assembly: AssemblyVersion(\"1.6.*\")", current)
        self.assertEqual("assembly: AssemblyVersion(\"1.0.0\")", new)


class FakeBranchProvider:
    def __init__(self):
        self.candidate_version = "1.0.0"
        self.latest_version = "latest-version"
        self.candidate_branch = "new-candidate"