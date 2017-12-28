import unittest
import re
from pyfakefs import fake_filesystem
from release_ccharp.snpseq_paths import SnpseqPathProperties
from release_ccharp.snpseq_paths import SnpseqPathActions
from tests.unit.utility.fake_os_service import FakeOsService


class SnpseqPathActionsTests(unittest.TestCase):
    def setUp(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "chiasma",
            "owner": "GitEdvard"
        }
        filesystem = fake_filesystem.FakeFilesystem()
        self.path_properties = SnpseqPathProperties(config, "chiasma")
        self.path_properties.branch_provider = FakeBranchProvider()
        self.path_actions = SnpseqPathActions(whatif=False, snpseq_path_properties=self.path_properties,
                                              os_service=FakeOsService(filesystem))

    def test_find_version_from_candidate_path__with_release_candidate__returns_ok(self):
        candidate_path = r'P:\lims\chiasma\candidates\release-1.18.0\build123\chiasma.exe'
        version = self.path_actions.find_version_from_candidate_path(candidate_path)
        self.assertEqual('1.18.0', version)

    def test_regex(self):
        text = r'a\release-1.0.0\b'
        res = re.match(r'.*(release)-(\d+)\.(\d+)\.(\d+).*', text)
        version = '{}.{}.{}'.format(res.group(2), res.group(3), res.group(4))
        self.assertEqual('1.0.0', version)


class FakeBranchProvider:
    def __init__(self):
        self.candidate_version = "1.0.0"
        self.latest_version = "latest-version"
        self.candidate_branch = "release-1.0.0"