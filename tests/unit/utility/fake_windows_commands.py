from pyfakefs.fake_filesystem import FakeOsModule


class FakeWindowsCommands:
    def __init__(self, filesystem):
        self.filesystem = filesystem
        self.os_module = FakeOsModule(filesystem)

    def build_solution(self):
        pass

    def create_shortcut(self, save_path, target_path):
        if not self.os_module.path.exists(save_path):
            self.filesystem.CreateFile(save_path)
