from __future__ import print_function
import os
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.exceptions import SnpseqXmlEntryNotFoundException
from release_ccharp.utils import UnexpectedLengthError
from release_ccharp.utils import lazyprop
from release_ccharp.utils import single


class SqatBuilder:
    def __init__(self, sqat, os_service, app_paths, file_deployer, binary_version_updater, windows_commands):
        self.sqat = sqat
        self.os_service = os_service
        self.app_paths = app_paths
        self.file_deployer = file_deployer
        self.binary_version_updater = binary_version_updater
        self.windows_commands = windows_commands

    def run(self):
        self.check_not_already_run()
        self.update_binary_version()
        self.build_solution()
        self.move_candidates()
        self.transform_config()

    def check_not_already_run(self):
        self.file_deployer.check_not_already_run()

    def update_binary_version(self):
        self.binary_version_updater.update_binary_version(self._assembly_file_path)

    def build_solution(self):
        self.windows_commands.build_solution(self.solution_file_path)

    def move_candidates(self):
        self.app_paths.common_move_candidates(self.sqat.project_root_dir)
        config_src = os.path.join(self.sqat.project_root_dir, 'SQATconfig.xml')
        connect_src = os.path.join(self.sqat.project_root_dir, 'SQATconnect.xml')
        config_dst_validation = os.path.join(self.app_paths.validation_dir, 'SQATconfig.xml')
        config_dst_production = os.path.join(self.app_paths.production_dir, 'SQATconfig.xml')
        connect_dst_validation = os.path.join(self.app_paths.validation_dir, 'SQATconnect.xml')
        connect_dst_production = os.path.join(self.app_paths.production_dir, 'SQATconnect.xml')

        self.os_service.copyfile(config_src, config_dst_validation)
        self.os_service.copyfile(config_src, config_dst_production)
        self.os_service.copyfile(connect_src, connect_dst_validation)
        self.os_service.copyfile(connect_src, connect_dst_production)

    def transform_config(self):
        self._transform_validation_connect_config()
        self._transform_production_connect_config()

    def _transform_production_connect_config(self):
        connect_file_path = os.path.join(self.app_paths.production_dir, 'SQATconnect.xml')
        self.sqat.save_backup_file(connect_file_path)
        with self.sqat.open_xml(connect_file_path) as xml:
            configXml = SqatConfigXml(xml)
            configXml.remove_connection('QC_devel')
            configXml.remove_connection('QC_practice')

    def _transform_validation_connect_config(self):
        connect_file_path = os.path.join(self.app_paths.validation_dir, 'SQATconnect.xml')
        self.sqat.save_backup_file(connect_file_path)
        with self.sqat.open_xml(connect_file_path) as xml:
            configXml = SqatConfigXml(xml)
            configXml.remove_connection('QC_1')

    @lazyprop
    def _assembly_file_path(self):
        assembly_file_path = os.path.join(self.sqat.project_root_dir, 'AssemblyInfo.cs')
        if not self.os_service.exists(assembly_file_path):
            raise SnpseqReleaseException(
                "The assembly info file could not be found {}".format(assembly_file_path))
        return assembly_file_path

    def _find_solution_file_name(self):
        application = self._application_path
        oss = self.os_service
        lst = [o for o in oss.listdir(application) if oss.isfile(os.path.join(application, o))]
        for file in lst:
            if file.endswith(".sln"):
                return file
        raise SnpseqReleaseException("The solution file could not be found, directory {}".format(application))

    @lazyprop
    def solution_file_path(self):
        return os.path.join(self._application_path, self._find_solution_file_name())

    @lazyprop
    def _application_path(self):
        download_dir = self.app_paths.download_dir
        return os.path.join(download_dir, 'application')


class SqatConfigXml:
    def __init__(self, tree_root):
        self.tree_root = tree_root
        self.connection_list = tree_root.findall('Connection')

    def get_connection_string(self, connection_name):
        node = self._get_node(connection_name)
        return node.find('ConnectionString').text

    def get_chiasma_connection_string(self, connection_name):
        node = self._get_node(connection_name)
        return node.find('ChiasmaConnectionString').text

    def remove_connection(self, connection_name):
        node = self._get_node(connection_name)
        self.tree_root.remove(node)

    def _get_node(self, connection_name):
        try:
            return single([n for n in self.connection_list if n.find('Name').text == connection_name])
        except UnexpectedLengthError:
            raise SnpseqXmlEntryNotFoundException('Entry for connection not found: {}'.format(connection_name))

