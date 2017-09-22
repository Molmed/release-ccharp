import unittest
from release_ccharp.snpseq_workflow import SnpseqWorkflow


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        # pass
        self.workflow = SnpseqWorkflow(whatif=False, repo='testing-repo')

    @unittest.skip("")
    def test_create_cand(self):
        self.workflow.create_cand()
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_download(self):
        self.workflow.download()
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_generate_manual(self):
        self.workflow.generate_user_manual()
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_copy_manual(self):
        self.workflow.copy_previous_user_manual()

    @unittest.skip("")
    def test_accept(self):
        self.workflow.accept()
        self.assertEqual(1,2)

    @unittest.skip("")
    def test_download_release_history(self):
        self.workflow.download_release_history()
        self.assertEqual(1,2)
