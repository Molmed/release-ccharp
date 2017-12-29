from __future__ import print_function
from release_ccharp.apps.common.single_file_read_write import BinaryVersionUpdater
from release_ccharp.apps.common.base import ApplicationBase
from release_ccharp.apps.common.directory_handling import ValidationDeployer
from release_ccharp.apps.chiasma_scripts.builder import ChiasmaBuilder
from release_ccharp.apps.chiasma_scripts.validation_deployer import ChiasmaValidationDeployer
from release_ccharp.apps.chiasma_scripts.deployer import ChiasmaDeployer


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
        self.validation_deployer = ChiasmaValidationDeployer(self, validation_deployer)
        self.deployer = ChiasmaDeployer(self.path_properties, self.app_paths, os_service)

    def build(self):
        self.chiasma_builder.run()

    def deploy_validation(self):
        self.validation_deployer.run()

    def deploy(self):
        self.deployer.run()
