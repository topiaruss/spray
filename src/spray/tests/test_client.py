import unittest
from spray import client
from spray import matrix
from spray import SPRAY_ROOT


class TestAssembler(unittest.TestCase):

    def test_assembler_inst(self):
        mm = matrix.CSVActionMatrix(SPRAY_ROOT + '/doc/tests/System Event-Action matrix - Matrix.csv')
        ass = client.Assembler(mm, 'system.project.drafted', {})
        assert ass  # fool syntax checker

    def test_assembler_body_fields(self):
        mm = matrix.CSVActionMatrix(SPRAY_ROOT + '/doc/tests/System Event-Action matrix - Matrix.csv')
        ass = client.Assembler(mm, '', {})
        ff = ass.get_undef_body_fields("{{test}}")
        self.assertEqual(ff, ('test',))

    def test_assembler_body_fields_syntax_error(self):
        mm = matrix.CSVActionMatrix(SPRAY_ROOT + '/doc/tests/System Event-Action matrix - Matrix.csv')
        ass = client.Assembler(mm, '', {})
        ff = ass.get_undef_body_fields("{{test}")
        self.assertEqual(ff, None)
        import pdb; pdb.set_trace()
        self.assertEqual(ass.syntax_error, ("unexpected '}'", "line: 1"))
        self.assertEqual(ass.broken_template, "{{test}")

