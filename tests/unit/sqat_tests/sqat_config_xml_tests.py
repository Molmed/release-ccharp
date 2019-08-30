from __future__ import print_function
import unittest
from release_ccharp.apps.sqat_scripts.builder import SqatConfigXml
from tests.unit.utility.config import SQAT_CONNECT
from tests.unit.utility.fake_os_service import FakeOsService
from tests.unit.sqat_tests.base import SqatBaseTests


class SqatConfigXmlTests(SqatBaseTests):
    def setUp(self):
        self.setup_sqat()
        self.connect_file_path = r'c:\xxx\connect.xml'
        self.filesystem.create_file(self.connect_file_path, contents=SQAT_CONNECT)

    def test_get_production_connection__with_original_connect_file__connection_string_achieved(self):
        # Arrange
        # Act
        # Assert
        with self.sqat.open_xml(self.connect_file_path) as xml:
            configXml = SqatConfigXml(xml)
            connection_string = configXml.get_connection_string('QC_1')
            self.assertEqual('data source=mm-wchs001;integrated security=true;initial catalog=QC_1;',
                             connection_string)

    def test_get_production_connection__with_original_connect_file__chiasma_connection_string_achieved(self):
        # Arrange
        # Act
        # Assert
        with self.sqat.open_xml(self.connect_file_path) as xml:
            configXml = SqatConfigXml(xml)
            connection_string = configXml.get_chiasma_connection_string('QC_1')
            self.assertEqual('data source=mm-wchs001;integrated security=true;initial catalog=GTDB2;',
                             connection_string)
