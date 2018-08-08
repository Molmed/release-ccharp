from __future__ import print_function
import unittest
from release_ccharp.apps.chiasmadeposit import Application
from release_ccharp.utility.os_service import OsService
from release_ccharp.snpseq_workflow import SnpseqWorkflow
from release_ccharp.apps.common.base import WindowsCommands


class ChiasmaDepositTests(unittest.TestCase):
    def test_build_solution(self):
        # Arrange
        path2 = r'C:\GitRoot\ChiasmaDeposit\ChiasmaDeposit1.sln'
        path = r'C:\Tmp2\Molmed-ChiasmaDeposit-9b13e94\ChiasmaDeposit1.sln'
        path3 = r'C:\GitRoot\chiasma\Chiasma.sln'
        windows_commands = WindowsCommands()

        # Act
        windows_commands.build_solution(path)
