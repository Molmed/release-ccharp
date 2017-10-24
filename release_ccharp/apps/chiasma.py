from __future__ import print_function
import os
from shutil import copyfile
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.apps.common import BinaryVersionUpdater
from release_ccharp.apps.common import StandardVSConfigXML
from release_ccharp.apps.common import ApplicationBase


class Application(ApplicationBase):
    """
    Code that is specific to the Chiasma application
    It needs snpseq-workflow because the latest and candidate version
    is fetch through the github provider (in the workflow)
    """
    def __init__(self, snpseq_workflow, branch_provider, os_service, whatif):
        super(Application, self).__init__(snpseq_workflow, branch_provider, os_service, whatif)
        self.binary_version_updater = BinaryVersionUpdater(
            whatif=False, config=self.config, path_properties=self.path_properties,
            branch_provider=branch_provider, app_paths=self.app_paths, os_service=os_service)

    def build(self):
        self.check_build_not_already_run()
        self.update_binary_version()
        self.build_solution()
        self.move_candidates()
        self.transform_config()

    def update_binary_version(self):
        self.binary_version_updater.update_binary_version()

    def check_build_not_already_run(self):
        if os.path.exists(self.app_paths.production_dir) or \
                os.path.exists(self.app_paths.validation_dir):
            raise SnpseqReleaseException(
                ("Production or validation catalog already exists. " 
                "They need to be removed before continuing"))

    def build_solution(self):
        self.builder.build_solution()

    def move_candidates(self):
        self.app_paths.move_candidates()

    def _transform_config(self, directory):
        config_file_path = os.path.join(directory, self.app_paths.config_file_name)
        db_name = "GTDB2" if directory == self.app_paths.production_dir else "GTDB2_practice"
        with self.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "Molmed.Chiasma")
            config.update("EnforceAppVersion", "True")
            config.update("DilutePlateAutomaticLabelPrint", "True")
            config.update("DiluteTubeAutomaticLabelPrint", "True")
            config.update("DebugMode", "False")
            config.update("DatabaseName", db_name)
        lab_config_dir = os.path.join(directory, "Config_lab")
        path_actions = SnpseqPathActions(whatif=self.whatif,
                                         snpseq_path_properties=self.path_properties,
                                         os_service=self.os_service)
        path_actions.create_dirs(lab_config_dir)
        lab_config_file_path = os.path.join(lab_config_dir, self.app_paths.config_file_name)
        self.os_service.copyfile(config_file_path, lab_config_file_path)
        with self.open_xml(lab_config_file_path, backup_origfile=False) as xml:
            config = StandardVSConfigXML(xml, "Molmed.Chiasma")
            config.update("ApplicationMode", "LAB")

    def transform_config(self):
        self._transform_config(self.app_paths.production_dir)
        self._transform_config(self.app_paths.validation_dir)
