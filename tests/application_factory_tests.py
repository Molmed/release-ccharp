from __future__ import print_function
import unittest
from release_ccharp.apps.common import ApplicationFactory


class ApplicationFactoryTests(unittest.TestCase):
    def setUp(self):
        self.factory = ApplicationFactory()

    def test_initiate_chiasma(self):
        instance = self.factory.get_instance(False, "chiasma")
        self.assertTrue(getattr(instance, "build"))

    def test_initiate_testing_repo(self):
        instance = self.factory.get_instance(False, "testing-repo")
        self.assertTrue(getattr(instance, "build"))
