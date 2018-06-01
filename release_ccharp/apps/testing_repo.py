from __future__ import print_function
from release_ccharp.apps.common.single_file_read_write import BinaryVersionUpdater
from release_ccharp.apps.common.base import ApplicationBase
from release_ccharp.apps.common.directory_handling import FileDeployer
from release_ccharp.apps.chiasma_scripts.builder import ChiasmaBuilder
from release_ccharp.apps.chiasma_deposit_scripts.builder import ChiasmaDepositBuilder
from release_ccharp.apps.sqat_scripts.builder import SqatBuilder
from release_ccharp.apps.chiasma_scripts.validation_deployer import ChiasmaValidationDeployer
from release_ccharp.apps.chiasma_deposit_scripts.validation_deployer import ChiasmaDepositValidationDeployer
from release_ccharp.apps.sqat_scripts.validation_deployer import SqatValidationDeployer
from release_ccharp.apps.chiasma_scripts.deployer import ChiasmaDeployer
from release_ccharp.apps.chiasma_deposit_scripts.deployer import ChiasmaDepositDeployer
from release_ccharp.apps.sqat_scripts.deployer import SqatDeployer
from release_ccharp.apps.common.single_file_read_write import ShortcutExaminer
from release_ccharp.apps.fp_scripts.builder import FPBuilder
from release_ccharp.apps.fp_scripts.validation_deployer import FPValidationDeployer
from release_ccharp.apps.fp_scripts.deployer import FPDeployer
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.apps.sqat import Application as SqatApplication


class Application(ApplicationBase):
    """
    Uses the chiasma code for testing purposes. Uses a local folder tree
    """
    def __init__(self, snpseq_workflow, branch_provider, os_service, windows_commands, whatif):
        super(Application, self).__init__(snpseq_workflow, branch_provider, os_service,
                                          windows_commands, whatif)
        self.binary_version_updater = BinaryVersionUpdater(
            whatif=False, config=self.config, path_properties=self.path_properties,
            branch_provider=branch_provider, app_paths=self.app_paths, os_service=os_service)
        file_deployer = FileDeployer(
            self.path_properties, self.os_service, snpseq_workflow.config, self.app_paths)
        self.chiasma_deposit_builder = ChiasmaDepositBuilder(self, file_deployer, self.app_paths, self.config)
        path_actions = SnpseqPathActions(
            whatif, self.path_properties, os_service, self.app_paths, self.windows_commands)
        self.validation_deployer = ChiasmaDepositValidationDeployer(
            self, file_deployer, path_actions)
        self.deployer = ChiasmaDepositDeployer(
            self.path_properties, file_deployer, path_actions, branch_provider)

    def build(self):
        super(Application, self).build()
        self.chiasma_deposit_builder.run()

    def deploy_validation(self):
        super(Application, self).deploy_validation()
        self.validation_deployer.run()

    def deploy(self, skip_copy_backup):
        super(Application, self).deploy(skip_copy_backup)
        self.deployer.run()

    def download_release_history(self):
        super(Application, self).download_release_history()
        self.snpseq_workflow.download_release_history()
        self.deployer.copy_release_history()
