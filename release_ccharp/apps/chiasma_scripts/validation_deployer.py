from __future__ import print_function
import os


class ChiasmaValidationDeployer:
    def __init__(self, chiasma):
        self.chiasma = chiasma
        self.os_service = chiasma.os_service

    def run(self):
        pass

    def create_shortcut(self):
        source = os.path.join(self.chiasma.app_paths.validation_dir, 'Chiasma.exe')
        dest = os.path.join(self.chiasma.path_properties.user_validation_latest, 'Chiasma.lnk')

