import os
from release_ccharp.apps.chiasma import Application
from release_ccharp.utils import create_dirs
from tests.unit.utility.fake_windows_commands import FakeWindowsCommands
from tests.unit.base import BaseTests


class ChiasmaBaseTests(BaseTests):
    def setup_chiasma(self):
        config = {
            "root_path": r'c:\xxx',
            "local_root_path": r'c:\local',
            "git_repo_name": "chiasma",
            "exe_file_name_base": "Chiasma",
            "project_root_dir" : "Chiasma",
            'db_backup_server_dir' : r'server_dir',
            'db_backup_filename' : 'gtdb2_devel_backup.bak',
            "owner": "GitEdvard",
            "deploy_root_path": r'c:\xxx\deploy'
        }
        wf, branch_provider, os_service = self.base_setup(config, 'chiasma')
        self.os_service = os_service
        self.chiasma = Application(wf, branch_provider, os_service,
                                   FakeWindowsCommands(self.filesystem), whatif=False)
        path = r'c:\local\chiasma\candidates\release-1.0.0\GitEdvard-chiasma-123\DatabaseDelivery\bin\release'
        database_delivery_path = os.path.join(
            path, r'DatabaseDelivery.exe'
        )
        create_dirs(os_service, path, False, False)
        self.filesystem.create_file(database_delivery_path, contents='none')
