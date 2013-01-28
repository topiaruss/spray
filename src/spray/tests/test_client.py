import unittest
from spray import client
from spray import matrix
from spray import SPRAY_ROOT


class TestAssembler(unittest.TestCase):

    def test_assembler_inst(self):
        mm = matrix.CSVActionMatrix(SPRAY_ROOT + '/doc/tests/System Event-Action matrix - Matrix.csv')
        ass = client.Assembler(mm, 'system.project.drafted', {})
        assert ass  # fool syntax checker



