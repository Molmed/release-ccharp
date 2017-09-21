import unittest
from release_ccharp.snpseq_workflow import SnpseqWorkflow
import yaml
import os
import re


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        # pass
        self.workflow = SnpseqWorkflow(whatif=False, repo='testing-repo')

    def test_yaml(self):
        with open(r'c:\gitroot\release-ccharp\release_ccharp\release_ccharp.config', 'r') as f:
            obj = yaml.load(f)
        print obj['testing-repo']
        self.assertEqual(1,1)

    @unittest.skip("")
    def test_create_cand(self):
        self.workflow.create_cand()
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_download(self):
        self.workflow.download()
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_accept(self):
        self.workflow.accept()
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_download_release_history(self):
        self.workflow.download_release_history()
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_find_directories(self):
        download_path = self.workflow.config[self.workflow.repo]['download_path']
        subentries = os.listdir(download_path)
        for entry in subentries:
            path_for_entry = os.path.join(download_path, entry)
            if os.path.isdir(path_for_entry):
                print entry
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_match_regex(self):
        m = re.match('(release|hotfix)-2.1.0', 'release-2.1.0')
        if m:
            print "match"
        else:
            print "not matching"
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_generate_manual(self):
        self.workflow.generate_user_manual()
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_find_current_release_dir(self):
        wf = self.workflow._create_workflow()
        path = self.workflow.paths.find_current_candidate_dir(workflow=wf)
        self.assertEqual("xxx", path)

    @unittest.skip("")
    def test_get_current_release_tag(self):
        wf = self.workflow._create_workflow()
        tag = self.workflow.paths._candidate_tag(wf)
        self.assertEqual("xxx", tag)

    def test_copy_manual(self):
        self.workflow.copy_previous_user_manual()