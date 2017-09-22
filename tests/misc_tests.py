import unittest
import os
import yaml
from release_ccharp.snpseq_workflow import SnpseqWorkflow


class MiscTests(unittest.TestCase):
    def setUp(self):
        self.workflow = SnpseqWorkflow(whatif=False, repo='testing-repo')

    @unittest.skip("")
    def test_yaml(self):
        with open(r'c:\gitroot\release-ccharp\release_ccharp\repo.config', 'r') as f:
            obj = yaml.load(f)
        print obj['testing-repo']
        self.assertEqual(1,1)

    @unittest.skip("")
    def test_find_directories(self):
        download_path = self.workflow.config['download_path']
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
