from __future__ import print_function
import os
import re
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.apps.common.single_file_read_write import StandardVSConfigXML
from release_ccharp.utils import create_dirs


class FPBuilder:
    def __init__(self, fp, file_deployer, app_paths, config, os_service, windows_commands):
        self.fp = fp
        self.file_deployer = file_deployer
        self.app_paths = app_paths
        self.os_service = os_service
        self.config = config
        self.windows_commands = windows_commands
        self.config_transformer = ConfigTransformer(fp, app_paths, os_service)

    def run(self):
        self.check_build_not_already_run()
        self.update_binary_version()
        self.build_solution()
        self.move_candidates()
        self.config_transformer.run()

    def check_build_not_already_run(self):
        self.file_deployer.check_not_already_run()

    def update_binary_version(self):
        assembly_file_path = self._assembly_file_path
        self.fp.binary_version_updater.update_binary_version(assembly_file_path)

    @property
    def _assembly_file_path(self):
        assembly_subpath = os.path.join(self.config["project_root_dir"], 'assemblyinfo.vb')
        assembly_file_path = os.path.join(
            self.app_paths.download_dir, assembly_subpath)
        if not self.os_service.exists(assembly_file_path):
            raise SnpseqReleaseException(
                "The assembly info file could not be found {}".format(assembly_file_path))
        return assembly_file_path

    def build_solution(self):
        solution_file_path = self._find_solution_file()
        self.windows_commands.build_solution(solution_file_path)

    def _find_solution_file(self):
        download_dir = self.app_paths.download_dir
        project_root_dir = os.path.join(download_dir, self.config['project_root_dir'])
        oss = self.os_service
        lst = [o for o in oss.listdir(project_root_dir) if oss.isfile(os.path.join(project_root_dir, o))]
        file_list = [f for f in lst if f.endswith('.sln')]
        if len(file_list) != 1:
            raise SnpseqReleaseException("The solution file could not be found, directory {}".format(project_root_dir))
        return os.path.join(project_root_dir, file_list[0])

    def move_candidates(self):
        project_root_path = os.path.join(self.app_paths.download_dir,
                                         self.config['project_root_dir'])
        bin_dir = os.path.join(project_root_path, 'bin')
        self.os_service.copytree(bin_dir, self.app_paths.validation_dir)
        self.os_service.copytree(bin_dir, self.app_paths.production_dir)
        txt_config_file = os.path.join(project_root_path, 'fpdatabaseconfig.txt')
        dst_validation = os.path.join(self.app_paths.validation_dir, 'FPDatabaseConfig.txt')
        self.os_service.copyfile(txt_config_file, dst_validation)
        dst_production = os.path.join(self.app_paths.production_dir, 'FPDatabaseConfig.txt')
        self.os_service.copyfile(txt_config_file, dst_production)


class ConfigTransformer:
    def __init__(self, fp, app_paths, os_service):
        self.fp = fp
        self.app_paths = app_paths
        self.os_service = os_service

    def run(self):
        self._transform_configs(self.app_paths.production_dir)
        self._transform_configs(self.app_paths.validation_dir)

    def _transform_xml_config(self, directory):
        config_file_path = os.path.join(directory, self.app_paths.config_file_name)
        self.fp.save_backup_file(config_file_path)
        with self.fp.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "FPDatabase")
            config.update("EnforceAppVersion", "True")

    def _transform_txt_config(self, directory):
        fp_db_name = "FP" if directory == self.app_paths.production_dir else "FP_practice"
        chiasma_db_name = 'GTDB2' if directory == self.app_paths.production_dir else 'GTDB2_practice'
        config_filename = os.path.join(directory, 'FPDatabaseConfig.txt')
        with self.os_service.open(config_filename, 'r') as f:
            contents = f.read()
        fp_replace = self._transform_txt_fp_replace(contents, fp_db_name)
        chiasma_replace = self._transform_txt_gtdb2_replace(fp_replace, chiasma_db_name)
        with self.os_service.open(config_filename, 'w') as f:
            f.write(chiasma_replace)

    def _transform_txt_fp_replace(self, orig_contents, fp_db_name):
        m = re.match('(.*fpconnectionstring.*?);initial catalog.+?;(.*)', orig_contents, re.IGNORECASE | re.DOTALL)
        return '{};initial catalog={};{}'.format(m.group(1), fp_db_name, m.group(2))

    def _transform_txt_gtdb2_replace(self, orig_contents, fp_db_name):
        m = re.match('(.*chiasmaconnectionstring.*?);initial catalog.+?;(.*)', orig_contents, re.IGNORECASE | re.DOTALL)
        return '{};initial catalog={};{}'.format(m.group(1), fp_db_name, m.group(2))

    def _transform_configs(self, directory):
        self._transform_xml_config(directory)
        self._transform_txt_config(directory)
