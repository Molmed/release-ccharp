from __future__ import print_function
from release_ccharp.apps.sqat import Application
from tests.unit.utility.fake_windows_commands import FakeWindowsCommands
from tests.unit.base import BaseTests


class SqatBaseTests(BaseTests):
    def setup_sqat(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "sqat",
            "exe_file_name_base": "sqat",
            "project_root_dir" : "sqat",
            "owner": "GitEdvard",
            "deploy_root_path": r'c:\xxx\deploy'
        }
        wf, branch_provider, os_service = self.base_setup(config, 'sqat')
        self.os_service = os_service
        self.sqat = Application(wf, branch_provider, os_service,
                                   FakeWindowsCommands(self.filesystem), whatif=False)

