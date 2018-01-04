from __future__ import print_function
from unittest import skip
from release_ccharp.utils import create_dirs
from release_ccharp.exceptions import SnpseqReleaseException
from tests.unit.sqat_tests.base import SqatBaseTests


class SqatBuildTests(SqatBaseTests):
    def setUp(self):
        self.setup_sqat()

    def test_check_not_already_run__with_production_catalog_existing__throws(self):
        # Arrange
        create_dirs(self.os_service, r'c:\xxx\sqat\candidates\release-1.0.0\production')

        # Act
        # Assert
        with self.assertRaises(SnpseqReleaseException):
            self.sqat.builder.check_not_already_run()


class FileBuilder:
    def __init__(self, filesystem):
        self.filesystem = filesystem

