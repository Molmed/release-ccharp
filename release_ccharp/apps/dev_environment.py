from __future__ import print_function
import os
from release_ccharp.snpseq_paths import SnpseqPathProperties
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.snpseq_workflow import SnpseqWorkflow


class TestEnvironmentProvider:
    def __init__(self):
        self.candidate_folder = "new-candidate"

    def generate(self, config):
        # Prepare
        path_properites = SnpseqPathProperties(config, config["git_repo_name"])
        path_actions = SnpseqPathActions(whatif=False, snpseq_path_properties=path_properites)
        wf = SnpseqWorkflow(whatif=False, repo=config["git_repo_name"])
        wf.config = config
        branch = "master"
        cand_path = os.path.join(path_properites.candidate_root_path, self.candidate_folder)

        # Actions
        path_actions.generate_folder_tree()
        path_actions.create_dirs(cand_path)
        wf.workflow.provider.download_archive(branch, cand_path)