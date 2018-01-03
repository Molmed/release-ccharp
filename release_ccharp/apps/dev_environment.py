from __future__ import print_function
import os
from release_ccharp.snpseq_paths import SnpseqPathProperties
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.utility.os_service import OsService


class TestEnvironmentProvider:
    def __init__(self):
        self.candidate_folder = "new-candidate"

    def generate(self, config):
        # Prepare
        path_properites = SnpseqPathProperties(config, config["git_repo_name"], OsService())
        path_actions = SnpseqPathActions(whatif=False, path_properties=path_properites,
                                         os_service=OsService())
        wf = SnpseqWorkflow(whatif=False, repo=config["git_repo_name"], os_service=OsService())
        wf.config = config
        branch = "master"
        cand_path = os.path.join(path_properites.root_candidates, self.candidate_folder)

        # Actions
        path_actions.generate_folder_tree()
        path_actions.create_dirs(cand_path)
        wf.workflow.provider.download_archive(branch, cand_path)
