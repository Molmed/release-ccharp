import unittest
from unittest import skip
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ElementTree, Element, SubElement, QName, tostring
from pyfakefs import fake_filesystem
from release_ccharp.apps.common.single_file_read_write import VsConfigOpener
from release_ccharp.apps.common.single_file_read_write import StandardVSConfigXML
from tests.unit.utility.config import CHIASMA_CONFIG
from tests.unit.utility.config import CHIASMA_CONFIG_REPLACE_TEST
from tests.unit.utility.config import CHIASMA_CONFIG_TRANSFORMED
from release_ccharp.apps.common.base import ApplicationBase
from tests.unit.chiasma_tests.base import ChiasmaBaseTests
from tests.unit.utility.helpers import copy_to_clipboard
from tests.unit.utility.fake_os_service import FakeOsService
from release_ccharp.utils import create_dirs


class TestCopyTree(ChiasmaBaseTests):
    def setUp(self):
        self.setup_chiasma()
        chiasma_config_path = (r'c:\xxx\chiasma\candidates\validation\chiasma.exe.config')
        self.filesystem.create_file(chiasma_config_path, contents=CHIASMA_CONFIG)

    def test_write_xml(self):
        myns = 'http://myns.com'
        top = Element('top')
        foo = SubElement(top, '{http://unique.com}foo')

        print(tostring(top))
        self.assertEqual(1, 1)

    def test_write_settings_section(self):
        config_file_path = r'c:\xxx\chiasma\candidates\validation\chiasma.exe.config'
        with self.chiasma.open_xml(config_file_path) as xml:
            config = StandardVSConfigXML(xml, "Molmed.Chiasma.Properties")
            settings_list = config.setting_list
        node_list = [tostring(s) for s in settings_list]
        for n in node_list:
            print(n)
        self.assertEqual(1, 1)

    def test_replace_settings_section(self):
        del1 = '<Molmed.Chiasma.Properties.Settings>'
        del2 = '</Molmed.Chiasma.Properties.Settings>'
        config_start = CHIASMA_CONFIG.decode('utf-8-sig')
        first_part, second_part = config_start.split(del1)
        _, last_part = second_part.split(del2)
        transformed_xml = first_part + del1 + '\nreplacement text' + del2 + last_part
        transformed_xml = transformed_xml.encode('utf-8')
        self.assertEqual(CHIASMA_CONFIG_REPLACE_TEST, transformed_xml)

    def test_open_config(self):
        self.filesystem = fake_filesystem.FakeFilesystem()
        os_service = FakeOsService(self.filesystem)
        path= r'c:\xxx\configfile'
        create_dirs(os_service, r'c:\xxx')
        self.filesystem.create_file(path, contents=CHIASMA_CONFIG)
        vs_config_opener = VsConfigOpener(os_service, None, "Molmed.Chiasma.Properties")
        with vs_config_opener.open(path) as c:
            c.update("EnforceAppVersion", "True")
        with os_service.open(path, 'r') as f:
            contents = f.read()
        copy_to_clipboard(contents)
        expected = ''.join(CHIASMA_CONFIG_TRANSFORMED.split())
        actual = ''.join(contents.split())
        self.assertEqual(expected, actual)
