from release_ccharp.apps.order import Application
from tests.unit.utility.fake_windows_commands import FakeWindowsCommands
from tests.unit.base import BaseTests


class OrderBaseTests(BaseTests):
    def setup_order(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "order",
            "exe_file_name_base": "Order",
            "project_root_dir" : "PlattformOrdMan",
            'db_backup_server_dir' : r'server_dir',
            'db_backup_filename' : 'bookkeeping_devel_backup.bak',
            "owner": "GitEdvard",
            "deploy_root_path": r'c:\xxx\deploy'
        }
        wf, branch_provider, os_service = self.base_setup(config, 'order')
        self.os_service = os_service
        self.order = Application(wf, branch_provider, os_service,
                                   FakeWindowsCommands(self.filesystem), whatif=False)
