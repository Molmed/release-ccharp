from __future__ import print_function
import os
from release_ccharp.apps.common.base import ApplicationBase
from release_ccharp.apps.common.directory_handling import FileDeployer
from release_ccharp.apps.common.single_file_read_write import BinaryVersionUpdater
from release_ccharp.apps.sqat_scripts.builder import SqatBuilder


class Application(ApplicationBase):
    """
    Code that is specific to the SQAT application
    """
    def __init__(self, snpseq_workflow, branch_provider, os_service, windows_commands, whatif):
        super(Application, self).__init__(snpseq_workflow, branch_provider, os_service,
                                          windows_commands, whatif)
        binary_version_updater = BinaryVersionUpdater(
            whatif=False, config=self.config, path_properties=self.path_properties,
            branch_provider=branch_provider, app_paths=self.app_paths, os_service=os_service)
        file_deployer = FileDeployer(self.path_properties, os_service, self.config, self.app_paths)
        self.builder = SqatBuilder(self, os_service, self.app_paths, file_deployer,
                                   binary_version_updater, windows_commands)

    def build(self):
        super(Application, self).build()
        self.builder.run()

    def deploy_validation(self):
        super(Application, self).deploy_validation()

    def deploy(self):
        super(Application, self).deploy()

    def download_release_history(self):
        super(Application, self).download_release_history()

    @property
    def project_root_dir(self):
        application_path = os.path.join(self.app_paths.download_dir, 'application')
        return os.path.join(application_path, self.config['project_root_dir'])
