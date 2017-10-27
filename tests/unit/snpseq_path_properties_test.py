import unittest
from release_ccharp.snpseq_paths import SnpseqPathProperties


class SnpseqPathPropertiesTests(unittest.TestCase):
    def setUp(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "chiasma",
            "owner": "GitEdvard"
        }
        self.path_properties = SnpseqPathProperties(config, "chiasma")
        self.path_properties.branch_provider = FakeBranchProvider()

    def test_validation_archive__with_branch_provider_as_below__path_is_right(self):
        path = self.path_properties.validation_archive_dir
        self.assertEqual(r'c:\xxx\chiasma\UserValidations\AllVersions\1.0.0', path)


class FakeBranchProvider:
    def __init__(self):
        self.candidate_version = "1.0.0"
        self.latest_version = "latest-version"
        self.candidate_branch = "release-1.0.0"