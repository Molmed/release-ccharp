from __future__ import print_function
from release_ccharp.apps.common.base import ApplicationBase
from release_ccharp.apps.sqat_scripts.builder import SqatBuilder
from release_ccharp.apps.common.directory_handling import FileDeployer


class Application(ApplicationBase):
    """
    Code that is specific to the SQAT application
    """
    def __init__(self, snpseq_workflow, branch_provider, os_service, windows_commands, whatif):
        super(Application, self).__init__(snpseq_workflow, branch_provider, os_service,
                                          windows_commands, whatif)
        file_deployer = FileDeployer(self.path_properties, os_service, self.config, self.app_paths)
        self.builder = SqatBuilder(os_service, self.app_paths, file_deployer)

    def build(self):
        super(Application, self).build()

    def deploy_validation(self):
        super(Application, self).deploy_validation()

    def deploy(self):
        super(Application, self).deploy()

    def download_release_history(self):
        super(Application, self).download_release_history()
