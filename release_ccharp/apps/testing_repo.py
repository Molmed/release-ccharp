from __future__ import print_function
from release_ccharp.apps.common.single_file_read_write import BinaryVersionUpdater
from release_ccharp.apps.common.base import ApplicationBase
from release_ccharp.apps.common.directory_handling import FileDeployer
from release_ccharp.apps.chiasma_scripts.builder import ChiasmaBuilder
from release_ccharp.apps.sqat_scripts.builder import SqatBuilder
from release_ccharp.apps.chiasma_scripts.validation_deployer import ChiasmaValidationDeployer
from release_ccharp.apps.sqat_scripts.validation_deployer import SqatValidationDeployer
from release_ccharp.apps.chiasma_scripts.deployer import ChiasmaDeployer
from release_ccharp.apps.sqat_scripts.deployer import SqatDeployer
from release_ccharp.apps.common.single_file_read_write import ShortcutExaminer
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

        sqat = SqatApplication(snpseq_workflow, branch_provider, os_service, windows_commands, False)

        # Todo: do something about sending sqat to sqat builder when testing, dangerous!
        self.sqat_builder = SqatBuilder(sqat, os_service, self.path_properties, self.app_paths,
                                        file_deployer, self.binary_version_updater, windows_commands)
        self.chiasma_builder = ChiasmaBuilder(self, file_deployer, self.app_paths, self.config)
        path_actions = SnpseqPathActions(
            whatif, self.path_properties, os_service, self.app_paths, self.windows_commands)
        self.chiasma_validation_deployer = ChiasmaValidationDeployer(
            self, file_deployer, path_actions)

        shortcut_examiner = ShortcutExaminer(
            branch_provider, os_service, windows_commands,
            file_deployer, self.path_properties.shortcut_path)


        self.sqat_validation_deployer = SqatValidationDeployer(
            self, file_deployer, path_actions, shortcut_examiner, os_service, self.path_properties)

        self.chiasma_deployer = ChiasmaDeployer(
            self.path_properties, file_deployer, path_actions, os_service, branch_provider)

        self.sqat_deployer = SqatDeployer(self.path_properties, file_deployer, path_actions,
                                          os_service, branch_provider)

    def build(self):
        super(Application, self).build()
        self.sqat_builder.run()

    def deploy_validation(self):
        super(Application, self).deploy_validation()
        self.sqat_validation_deployer.run()

    def deploy(self):
        super(Application, self).deploy()
        self.sqat_deployer.run()

    def download_release_history(self):
        super(Application, self).download_release_history()
        self.snpseq_workflow.download_release_history()
        self.sqat_deployer.copy_release_history()
