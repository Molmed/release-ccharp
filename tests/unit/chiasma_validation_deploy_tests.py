import unittest
from unittest import skip
from pyfakefs import fake_filesystem
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.apps.chiasma import Application
from tests.unit.utility.fake_os_service import FakeOsService


class ChiasmaValidationDeployTests(unittest.TestCase):
    def setUp(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "chiasma",
            "owner": "GitEdvard"
        }
        branch_provider = FakeBranchProvider()
        wf = SnpseqWorkflow(whatif=False, repo="chiasma")
        wf.config = config
        wf.paths.config = config
        wf.paths.branch_provider = branch_provider
        self.filesystem = fake_filesystem.FakeFilesystem()
        os_service = FakeOsService(self.filesystem)
        self.os_module = os_service.os_module
        self.chiasma = Application(wf, branch_provider, os_service, whatif=False)

        path_actions = SnpseqPathActions(False, self.chiasma.path_properties, os_service)
        path_actions.create_dirs(r'c:\xxx\chiasma\candidates\new-candidate\validation')
        path_actions.create_dirs(r'c:\xxx\chiasma\uservalidations\latest')

    def test_create_shortcut__with_latest_empty__something_is_copied_to_latest(self):
        self.chiasma.validation_deployer.create_shortcut()
        self.assertTrue(self.os_module.path.exists(r'c:\xxx\chiasma\uservalidations\latest\chiasma.lnk'))

    def test_create_shortcut__with_shortcut_exists_in_target__copy_without_error(self):
        fake_destination_link = r'c:\xxx\chiasma\uservalidations\latest\chiasma.lnk'
        self.filesystem.CreateFile(fake_destination_link)

        # Act
        self.chiasma.validation_deployer.create_shortcut()

        # Assert
        self.assertTrue(self.os_module.path.exists(r'c:\xxx\chiasma\uservalidations\latest\chiasma.lnk'))

    def test_create_shortcut__with_target_exists_in_candidates__extract_shortcut_target_works(self):
        # Arrange
        fake_target_path = r'c:\xxx\chiasma\candidates\new-candidate\validation\chiasma.exe'
        self.filesystem.CreateFile(fake_target_path)
        dest_shortcut_path = r'c:\xxx\chiasma\uservalidations\latest\chiasma.lnk'

        # Act
        self.chiasma.validation_deployer.create_shortcut()
        shortcut_target = self.chiasma.validation_deployer.extract_shortcut_target(dest_shortcut_path)

        #Assert
        self.assertEqual(r'c:\xxx\chiasma\candidates\new-candidate\validation\chiasma.exe', shortcut_target)


class FakeBranchProvider:
    def __init__(self):
        self.candidate_version = "1.0.0"
        self.latest_version = "latest-version"
        self.candidate_branch = "new-candidate"