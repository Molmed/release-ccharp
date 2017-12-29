from __future__ import print_function
from release_ccharp.apps.common.single_file_read_write import BinaryVersionUpdater
from release_ccharp.apps.common.base import ApplicationBase
from release_ccharp.apps.common.directory_handling import ValidationDeployer
from release_ccharp.apps.common.directory_handling import Deployer
from release_ccharp.apps.chiasma_scripts.builder import ChiasmaBuilder
from release_ccharp.apps.chiasma_scripts.validation_deployer import ChiasmaValidationDeployer
from release_ccharp.apps.chiasma_scripts.deployer import ChiasmaDeployer
from release_ccharp.snpseq_paths import SnpseqPathActions


class Application(ApplicationBase):
    """
    Code that is specific to the Chiasma application
    It needs snpseq-workflow because the latest and candidate version
    is fetched through the github provider (in the workflow)
    """
    def __init__(self, snpseq_workflow, branch_provider, os_service, windows_commands, whatif):
        super(Application, self).__init__(snpseq_workflow, branch_provider, os_service,
                                          windows_commands, whatif)
        self.binary_version_updater = BinaryVersionUpdater(
            whatif=False, config=self.config, path_properties=self.path_properties,
            branch_provider=branch_provider, app_paths=self.app_paths, os_service=os_service)
        self.chiasma_builder = ChiasmaBuilder(self)
        validation_deployer = ValidationDeployer(self.path_properties, self.os_service)
        path_actions = SnpseqPathActions(
            whatif, self.path_properties, os_service, self.app_paths, self.windows_commands)
        self.validation_deployer = ChiasmaValidationDeployer(
            self, validation_deployer, path_actions)
        common_deployer = Deployer(
            self.path_properties, os_service, snpseq_workflow.config, self.app_paths)
        self.deployer = ChiasmaDeployer(self.path_properties, common_deployer)

    def build(self):
        self.chiasma_builder.run()

    def deploy_validation(self):
        self.validation_deployer.run()

    def deploy(self):
        self.deployer.run()
