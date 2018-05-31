from release_ccharp.apps.chiasma_deposit import Application
from tests.unit.utility.fake_windows_commands import FakeWindowsCommands
from tests.unit.base import BaseTests


class ChiasmaDepositBaseTests(BaseTests):
    def setup_chiasma_deposit(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "ChiasmaDeposit",
            "exe_file_name_base": "ChiasmaDeposit",
            "project_root_dir" : "ChiasmaDeposit",
            "owner": "GitEdvard",
            "deploy_root_path": r'c:\xxx\deploy'
        }
        wf, branch_provider, os_service = self.base_setup(config, 'chiasmadeposit')
        self.os_service = os_service
        self.chiasma_deposit = Application(wf, branch_provider, os_service,
                                   FakeWindowsCommands(self.filesystem), whatif=False)
