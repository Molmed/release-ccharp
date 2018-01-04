from __future__ import print_function


class SqatBuilder:
    def __init__(self, os_service, app_paths, file_deployer):
        self.os_service = os_service
        self.app_paths = app_paths
        self.file_deployer = file_deployer

    def run(self):
        self.check_not_already_run()

    def check_not_already_run(self):
        self.file_deployer.check_not_already_run()
