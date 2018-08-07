from __future__ import print_function
import os
import abc
import importlib
from subprocess import call
from contextlib import contextmanager
from win32com.client import Dispatch
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.utility.os_service import OsService
from release_ccharp.apps.common.directory_handling import AppPaths


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

    def save_backup_file(self, path):
        orig_file_path = "{}.orig".format(path)
        if not os.path.exists(orig_file_path):
            self.log("Saving backup of original file: {}".format(orig_file_path))
            self.os_service.copyfile(path, orig_file_path)

    @contextmanager
    def open_xml(self, path):
        self.log("Updating xml file: {}".format(path), print_always=True)
        tree = self.os_service.et_parse(path)
        yield tree.getroot()
        self.os_service.et_write(tree, path)

    def log(self, msg, print_always=False):
        if self.whatif or print_always:
            print(msg)

    @abc.abstractmethod
    def build(self):
        print('Starting build')

    @abc.abstractmethod
    def deploy_validation(self):
        print('Starting deploy validation')

    @abc.abstractmethod
    def deploy(self, skip_copy_backup):
        print('Starting deploy')

    @abc.abstractmethod
    def download_release_history(self):
        print('Starting download release history')


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


class ApplicationFactory:
    def import_application(self, repo):
        repo = repo.replace("-", "_")
        module = "release_ccharp.apps.{}".format(repo)
        module_obj = importlib.import_module(module)
        return getattr(module_obj, "Application")

    def get_instance(self, whatif, repo):
        application = self.import_application(repo)
        wf = SnpseqWorkflow(whatif, repo, OsService())
        branch_provider = wf.paths.branch_provider
        return application(wf, branch_provider, OsService(), WindowsCommands(), whatif)


class LatestVersionExaminer:
    @abc.abstractmethod
    def version_in_latest(self):
        pass

    @abc.abstractmethod
    def is_candidate_in_latest(self):
        pass


class LogMixin:
    def execute_and_log(self, fcn, message=None):
        msg = message or '{}...'.format(fcn.__name__.replace('_', ' '))
        print(msg)
        fcn()
        print('ok')
