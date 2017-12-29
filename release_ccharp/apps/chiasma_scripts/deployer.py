from __future__ import print_function
import os


class ChiasmaDeployer:
    def __init__(self, path_properties, app_path, os_service):
        self.path_properties = path_properties
        self.app_paths = app_path
        self.os_service = os_service

    def run(self):
        self.check_source_files_exists()

    def check_source_files_exists(self):
        print('Check that source files exists ...')

        exe = os.path.join(self.app_paths.production_dir, 'Chiasma.exe')
        config = os.path.join(self.app_paths.production_dir, self.app_paths.config_file_name)
        config_lab = os.path.join(
            self.app_paths.production_config_lab_dir, self.app_paths.config_file_name)
        user_manual = self.path_properties.user_manual_download_path

        if not self.os_service.exists(exe):
            raise FileDoesNotExistsException(exe)
        if not self.os_service.exists(config):
            raise FileDoesNotExistsException(config)
        if not self.os_service.exists(config_lab):
            raise FileDoesNotExistsException(config_lab)
        if not self.os_service.exists(user_manual):
            raise FileDoesNotExistsException(user_manual)

        print('ok')


class FileDoesNotExistsException(Exception):
    pass
