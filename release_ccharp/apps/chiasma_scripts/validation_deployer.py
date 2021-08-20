from __future__ import print_function
from release_ccharp.apps.common.single_file_read_write import ShortcutExaminer
from subprocess import call


class ChiasmaValidationDeployer:
    def __init__(self, chiasma, file_deployer, path_actions, local_app_paths):
        self.chiasma = chiasma
        self.file_deployer = file_deployer
        self.os_service = file_deployer.os_service
        self.local_app_paths = local_app_paths
        self.shortcut_examiner = ShortcutExaminer(
            self.chiasma.branch_provider, self.os_service, self.chiasma.windows_commands,
            file_deployer, self.chiasma.path_properties.shortcut_path)
        self.path_actions = path_actions

    def run(self):
        self.copy_validation_files()
        self.path_actions.create_shortcut_to_exe()
        self.update_database()

    def copy_validation_files(self):
        if not self.shortcut_examiner.is_candidate_in_latest:
            self.file_deployer.move_latest_to_archive(self.shortcut_examiner.version_in_latest)
        if self.os_service.exists(self.chiasma.path_properties.archive_dir_validation_files):
            self.file_deployer.back_move_from_archive()
        self.file_deployer.copy_to_latest()

    def update_database(self):
        self._update_database("devel")
        self._update_database("practice")

    def _update_database(self, destination):
        # destination: <devel|practice>
        database_delivery_path = self.local_app_paths.database_delivery_exe
        print("Calling DatabaseDelivery.exe to migrate {} db: \n{}"
              .format(destination, database_delivery_path))
        cmd = [database_delivery_path,
               destination]
        self.chiasma.windows_commands.call_subprocess(cmd)
        print('Done.')

