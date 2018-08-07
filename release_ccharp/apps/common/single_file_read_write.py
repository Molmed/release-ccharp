from __future__ import print_function
import os
import re
from release_ccharp.utils import single
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.apps.common.base import LatestVersionExaminer


class StandardVSConfigXML:
    def __init__(self, tree_root, app_namespace):
        settings_node_name = "{}.Settings".format(app_namespace)
        self.setting_list = \
            tree_root.find('applicationSettings').find(settings_node_name).findall('setting')

    def update(self, key, value):
        node = single([n for n in self.setting_list if n.get('name') == key])
        node.find('value').text = value

    def update_and_log(self, key, value):
        node = single([n for n in self.setting_list if n.get('name') == key])
        if not node.find('value').text == value:
            print('Change entry {} to {}'.format(key, value))
        node.find('value').text = value

    def get(self, key):
        node = single([n for n in self.setting_list if n.get('name') == key])
        return node.find('value').text


class BinaryVersionUpdater:
    def __init__(self, whatif, config, path_properties, branch_provider, app_paths, os_service):
        self.config = config
        self.whatif = whatif
        self.path_properties = path_properties
        self.branch_provider = branch_provider
        self.app_paths = app_paths
        self.os_service = os_service

    def _save_assembly_backup(self, assembly_file_path):
        orig_file_path = "{}.orig".format(assembly_file_path)
        if not self.os_service.exists(orig_file_path):
            print("Saving backup of original file: {}".format(orig_file_path))
            self.os_service.copyfile(assembly_file_path, orig_file_path)

    def get_assembly_replace_strings(self, content, new_version):
        match = re.search("(assembly:\s+AssemblyVersion)\(\".+\"\)", content, re.IGNORECASE)
        if match is None:
            raise SnpseqReleaseException("AssemblyVersion could not be found in AssemblyInfo file")
        replace_string = match.group(0)
        leading_text = match.group(1)
        new_string = '{}(\"{}\")'.format(leading_text, new_version)
        return replace_string, new_string

    def update_binary_version(self, assembly_file_path):
        print("Updating assembly info file...")
        self._save_assembly_backup(assembly_file_path)
        with self.os_service.open(assembly_file_path, 'r') as f:
            content = f.read()
        version = self.branch_provider.candidate_version
        current, new = self.get_assembly_replace_strings(content, version)

        print("Replacing ")
        print(current)
        print("with")
        print(new)
        updated = content.replace(current, new)
        if not self.whatif:
            with self.os_service.open(assembly_file_path, 'w') as f:
                f.write(updated)


class ShortcutExaminer(LatestVersionExaminer):
    def __init__(self, branch_provider, os_service, windows_commands,
                 common_deployer, shortcut_path):
        self.branch_provider = branch_provider
        self.os_service = os_service
        self.windows_commands = windows_commands
        self.common_deployer = common_deployer
        self.shortcut_path = shortcut_path

    @property
    def version_in_latest(self):
        shortcut_target = self._extract_shortcut_target(self.shortcut_path)
        return self.common_deployer.extract_version_from_path(shortcut_target)

    def _extract_shortcut_target(self, shortcut_path):
        return self.windows_commands.extract_shortcut_target(shortcut_path)

    @property
    def is_candidate_in_latest(self):
        version_to_validate = self.branch_provider.candidate_version
        if self.os_service.exists(self.shortcut_path):
            return self.version_in_latest == version_to_validate
        else:
            return True
