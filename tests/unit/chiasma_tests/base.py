from release_ccharp.apps.chiasma import Application
from tests.unit.utility.fake_windows_commands import FakeWindowsCommands
from tests.unit.base import BaseTests


class ChiasmaBaseTests(BaseTests):
    def setup_chiasma(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "chiasma",
            "exe_file_name_base": "Chiasma",
            "project_root_dir" : "Chiasma",
            "owner": "GitEdvard",
            "deploy_root_path": r'c:\xxx\deploy'
        }
        wf, branch_provider, os_service = self.base_setup(config, 'chiasma')
        self.chiasma = Application(wf, branch_provider, os_service,
                                   FakeWindowsCommands(self.filesystem), whatif=False)
