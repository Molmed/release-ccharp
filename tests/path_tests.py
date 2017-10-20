import unittest
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.snpseq_paths import SnpseqPathActions
from release_ccharp.snpseq_paths import SnpseqPathProperties
from release_ccharp.config import Config


class PathTests(unittest.TestCase):

    def setUp(self):
        conf = Config()
        self.path_properties = SnpseqPathProperties(conf.open_config(repo='testing-repo'), repo='testing-repo')

    @unittest.skip("")
    def test_find_current_candidate_dir(self):
        path = self.path_properties.current_candidate_dir
        self.assertEqual("xxx", path)

    @unittest.skip("")
    def test_get_current_candidate_tag(self):
        tag = self.path_properties._candidate_tag
        self.assertEqual("xxx", tag)

    def test_init_paths(self):
        # instantiate workflow (and paths) in setUp
        pass

    @unittest.skip("")
    def test_get_root_path(self):
        root_path = self.path_properties._repo_root
        self.assertEqual("xxx", root_path)

    def test_generate_paths(self):
        generator = SnpseqPathActions(False, self.path_properties)
        generator.generate_folder_tree()
        self.assertEqual(1,2)
