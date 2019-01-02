from __future__ import print_function
import os
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.apps.common.single_file_read_write import VsConfigOpener
from release_ccharp.utils import create_dirs


class ChiasmaBuilder:
    def __init__(self, chiasma, file_deployer, app_paths, config):
        self.chiasma = chiasma
        self.file_deployer = file_deployer
        self.app_paths = app_paths
        self.config = config

    def run(self):
        self.check_build_not_already_run()
        self.update_binary_version()
        self.build_solution()
        self.move_candidates()
        self.transform_config()

    def update_binary_version(self):
        assembly_file_path = self.app_paths.common_assembly_file_path
        self.chiasma.binary_version_updater.update_binary_version(assembly_file_path)

    def check_build_not_already_run(self):
        self.file_deployer.check_not_already_run()

    def build_solution(self):
        solution_file = self._find_solution_file()
        solution_file_path = os.path.join(self.chiasma.app_paths.download_dir, solution_file)
        self.chiasma.windows_commands.build_solution(solution_file_path)

    def _find_solution_file(self):
        download_dir = self.chiasma.app_paths.download_dir
        lst = [o for o in os.listdir(download_dir) if os.path.isfile(os.path.join(download_dir, o))]
        for file in lst:
            if file.endswith(".sln"):
                return file
        raise SnpseqReleaseException("The solution file could not be found, directory {}".format(download_dir))

    def move_candidates(self):
        project_root_path = os.path.join(self.app_paths.download_dir,
                                         self.config['project_root_dir'])
        self.chiasma.app_paths.common_move_candidates(project_root_path)

    def _transform_config(self, directory, result_web_service):
        config_file_path = os.path.join(directory, self.chiasma.app_paths.config_file_name)
        self.chiasma.save_backup_file(config_file_path)
        vs_config = VsConfigOpener(self.chiasma.os_service, self.chiasma.log,
                                   "Molmed.Chiasma.Properties")
        with vs_config.open(config_file_path) as config:
            config.update("EnforceAppVersion", "True")
            config.update("DilutePlateAutomaticLabelPrint", "True")
            config.update("DiluteTubeAutomaticLabelPrint", "True")
            config.update("DebugMode", "False")
            config.update("RepositoryImplementation", "Ef")
            config.update("Chiasma_ResultWebServiceDevelopment_ResultWebService", result_web_service)
        lab_config_dir = os.path.join(directory, self.chiasma.path_properties.config_lab_subpath)
        create_dirs(self.chiasma.os_service, lab_config_dir, self.chiasma.whatif,
                    self.chiasma.whatif)
        lab_config_file_path = os.path.join(lab_config_dir, self.chiasma.app_paths.config_file_name)
        self.chiasma.os_service.copyfile(config_file_path, lab_config_file_path)
        vs_config = VsConfigOpener(self.chiasma.os_service, self.chiasma.log,
                                   "Molmed.Chiasma.Properties")
        with vs_config.open(lab_config_file_path) as config:
            config.update("ApplicationMode", "LAB")

    def _transform_shared_kernel_config(self, directory, db_name):
        config_file_path = os.path.join(directory, 'chiasma.sharedkernel.exe.config')

        self.chiasma.save_backup_file(config_file_path)
        vs_config = VsConfigOpener(self.chiasma.os_service, self.chiasma.log,
                                   "Chiasma.SharedKernel.Properties")
        with vs_config.open(config_file_path) as config:
            config.update("DatabaseName", db_name)

    def _transform_configs(self, directory):
        provider = TransformSettingsProvider(self.chiasma)
        db_name, result_web_service = provider.fetch_env_dependent_variables(directory)
        self._transform_config(directory, result_web_service)
        self._transform_shared_kernel_config(directory, db_name)

    def transform_config(self):
        self._transform_configs(self.chiasma.app_paths.production_dir)
        self._transform_configs(self.chiasma.app_paths.validation_dir)


class TransformSettingsProvider:
    def __init__(self, chiasma):
        self.chiasma = chiasma

    def fetch_env_dependent_variables(self, directory):
        if directory == self.chiasma.app_paths.production_dir:
            db_name = "GTDB2"
            result_web_service = self._web_result_service_production
        else:
            db_name = "GTDB2_practice"
            result_web_service = self._web_result_service_validation
        return db_name, result_web_service

    @property
    def _web_result_service_validation(self):
        return 'http://mm-wchs001:65204/ChiasmaResultServiceValidation/ResultWebService.asmx'

    @property
    def _web_result_service_production(self):
        return 'http://mm-wchs001:65200/ChiasmaResultService/ResultWebService.asmx'

