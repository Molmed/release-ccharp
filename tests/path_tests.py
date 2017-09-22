import unittest
from release_ccharp.snpseq_workflow import SnpseqWorkflow


class PathTests(unittest.TestCase):

    @unittest.skip("")
    def setUp(self):
        self.workflow = SnpseqWorkflow(whatif=False, repo='testing-repo')

    @unittest.skip("")
    def test_find_current_candidate_dir(self):
        path = self.workflow.paths.current_candidate_dir
        self.assertEqual("xxx", path)

    @unittest.skip("")
    def test_get_current_candidate_tag(self):
        tag = self.workflow.paths._candidate_tag
        self.assertEqual("xxx", tag)
