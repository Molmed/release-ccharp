from release_ccharp.apps.fp import Application
from release_ccharp.apps.fp_scripts.builder import ConfigTransformer
from tests.unit.utility.fake_windows_commands import FakeWindowsCommands
from tests.unit.base import BaseTests


class FPBaseTests(BaseTests):
    def setup_fp(self):
        config = {
            "root_path": r'c:\xxx',
            "git_repo_name": "fp",
            "exe_file_name_base": "FPDatabase",
            "project_root_dir" : "FPDatabase_SourceCode",
            "owner": "GitEdvard",
            "deploy_root_path": r'c:\xxx\deploy'
        }
        wf, branch_provider, os_service = self.base_setup(config, 'fp')
        self.os_service = os_service
        self.fp = Application(wf, branch_provider, os_service,
                                   FakeWindowsCommands(self.filesystem), whatif=False)
        self.config_transformer = ConfigTransformer(self.fp, self.fp.app_paths, os_service)
