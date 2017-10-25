from __future__ import print_function
import os
import re
import abc
import importlib
from subprocess import call
from contextlib import contextmanager
from win32com.client import Dispatch
from release_ccharp.utils import single
from release_ccharp.utils import lazyprop
from release_ccharp.exceptions import SnpseqReleaseException
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.utility.os_service import OsService


class ApplicationBase(object):
    def __init__(self, snpseq_workflow, branch_provider, os_service, windows_commands, whatif):
        self.snpseq_workflow = snpseq_workflow
        self.config = snpseq_workflow.config
        self.path_properties = snpseq_workflow.paths
        self.branch_provider = branch_provider
        self.whatif = whatif
        self.os_service = os_service
        self.app_paths = AppPaths(self.config, self.path_properties, os_service)
        self.windows_commands = windows_commands

    @contextmanager
    def open_xml(self, path, backup_origfile=True):
        orig_file_path = "{}.orig".format(path)
        self.log("Updating xml file: {}".format(path))
        if backup_origfile and not os.path.exists(orig_file_path):
            self.log("Saving backup of original file: {}".format(orig_file_path))
            self.os_service.copyfile(path, orig_file_path)
        tree = self.os_service.et_parse(path)
        yield tree.getroot()
        self.os_service.et_write(tree, path)

    def log(self, msg):
        if self.whatif:
            print(msg)

    @abc.abstractmethod
    def build(self):
        pass


class StandardVSConfigXML:
    def __init__(self, tree_root, app_namespace):
        settings_node_name = "{}.Properties.Settings".format(app_namespace)
        self.setting_list = \
            tree_root.find('applicationSettings').find(settings_node_name).findall('setting')

    def update(self, key, value):
        node = single([n for n in self.setting_list if n.get('name') == key])
        node.find('value').text = value

    def get(self, key):
        node = single([n for n in self.setting_list if n.get('name') == key])
        return node.find('value').text


class WindowsCommands:
    def build_solution(self, solution_file_path):
        build_path = r'C:\Program Files (x86)\MSBuild\14.0\Bin\MSBuild.exe'
        print("build on solution file: {}".format(solution_file_path))
        cmd = [build_path, solution_file_path,
               r'/p:WarningLevel=0',
               r'/verbosity:minimal',
               r'/p:Configuration=Release']
        call(cmd)

    def create_shortcut(self, save_path, target_path):
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(save_path)
        shortcut.TargetPath = target_path
        shortcut.save()

    def extract_shortcut_target(self, shortcut_path):
        shell = Dispatch('WScript.Shell')
        return shell.CreateShortCut(shortcut_path).TargetPath


class AppPaths:
    """
    Handles directories which is located under a specific candidate
    Also include path actions
    """
    # TODO: move to snpseq_paths?
    def __init__(self, config, path_properties, os_service):
        self.config = config
        self.path_properties = path_properties
        self.os_service = os_service

    def find_download_directory_name(self):
        candidate_dir = self.path_properties.current_candidate_dir
        pattern = "{}-{}".format(self.config["owner"], self.config["git_repo_name"])
        oss = self.os_service
        dir_lst = [o for o in oss.listdir(candidate_dir) if oss.isdir(os.path.join(candidate_dir, o))]
        for d in dir_lst:
            if pattern in d:
                return d
        return None

    @lazyprop
    def download_dir(self):
        return os.path.join(self.path_properties.current_candidate_dir,
                            self.find_download_directory_name())

    @lazyprop
    def validation_dir(self):
        cand_dir = self.path_properties.current_candidate_dir
        return os.path.join(cand_dir, "validation")

    @lazyprop
    def production_dir(self):
        cand_dir = self.path_properties.current_candidate_dir
        return os.path.join(cand_dir, "production")

    @lazyprop
    def config_file_name(self):
        return "{}.exe.config".format(self.config["git_repo_name"])

    def move_candidates(self):
        release_subdir = os.path.join(self.config["git_repo_name"], r'bin\release')
        release_dir = os.path.join(self.download_dir, release_subdir)
        self.os_service.copytree(release_dir, self.validation_dir)
        self.os_service.copytree(release_dir, self.production_dir)


class BinaryVersionUpdater:
    def __init__(self, whatif, config, path_properties, branch_provider, app_paths, os_service):
        self.config = config
        self.whatif = whatif
        self.path_properties = path_properties
        self.branch_provider = branch_provider
        self.app_paths = app_paths
        self.os_service = os_service

    @lazyprop
    def assembly_file_path(self):
        assembly_subpath = os.path.join(self.config["git_repo_name"], r'properties\assemblyinfo.cs')
        assembly_file_path = os.path.join(
            self.app_paths.download_dir, assembly_subpath)
        if not self.os_service.exists(assembly_file_path):
            raise SnpseqReleaseException(
                "The assembly info file could not be found {}".format(assembly_file_path))
        return assembly_file_path

    def _save_assembly_backup(self):
        orig_file_path = "{}.orig".format(self.assembly_file_path)
        if not self.os_service.exists(orig_file_path):
            print("Saving backup of original file: {}".format(orig_file_path))
            self.os_service.copyfile(self.assembly_file_path, orig_file_path)

    def get_assembly_replace_strings(self, content, new_version):
        match = re.search("assembly: AssemblyVersion\(\".+\"\)", content)
        if match is None:
            raise SnpseqReleaseException("AssemblyVersion could not be found in AssemblyInfo file")
        replace_string = match.group(0)
        new_string = "assembly: AssemblyVersion(\"{}\")".format(new_version)
        return replace_string, new_string

    def update_binary_version(self):
        print("Updating assembly info file...")
        self._save_assembly_backup()
        with self.os_service.open(self.assembly_file_path, 'r') as f:
            content = f.read()
        version = self.branch_provider.candidate_version
        current, new = self.get_assembly_replace_strings(content, version)

        print("Replacing ")
        print(current)
        print("with")
        print(new)
        updated = content.replace(current, new)
        if not self.whatif:
            with self.os_service.open(self.assembly_file_path, 'w') as f:
                f.write(updated)


class ApplicationFactory:
    def import_application(self, repo):
        repo = repo.replace("-", "_")
        module = "release_ccharp.apps.{}".format(repo)
        module_obj = importlib.import_module(module)
        return getattr(module_obj, "Application")

    def get_instance(self, whatif, repo):
        application = self.import_application(repo)
        wf = SnpseqWorkflow(whatif, repo)
        branch_provider = wf.paths.branch_provider
        return application(wf, branch_provider, OsService(), WindowsCommands(), whatif)