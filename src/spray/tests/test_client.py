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
        self.assertEqual(ass.syntax_error, (u"unexpected '}'", "line: 1",))
        self.assertEqual(ass.broken_template, "{{test}")

    def test_assembler_undef_addr_fields_single(self):
        mm = matrix.CSVActionMatrix(SPRAY_ROOT + '/doc/tests/System Event-Action matrix - Matrix.csv')
        mm.update()
        ass = client.Assembler(mm, '', {})
        fields = ass.get_undef_addr_fields('crafter.message.sent', 'email', 'follower, copy admins')
        self.assertEqual(fields, ['follower_email_address', 'copy admins_email_address'])

    def test_assembler_undef_addr_fields_multiple(self):
        "run through the matrix, see if anything breaks"
        mm = matrix.CSVActionMatrix(SPRAY_ROOT + '/doc/tests/System Event-Action matrix - Matrix.csv')
        mm.update()
        ass = client.Assembler(mm, '', {})
        for eid in mm.get_event_ids():
            rows = mm.get_rows_for_event(eid)
            for r in rows:
                fields = ass.get_undef_addr_fields(r['event_id'], r['action_type'], r['recipient'])
                assert fields
                #print r['event_id'], fields

    def test_assembler_field_tokens_multiple(self):
        "run through the matrix looking for field tokens, see if anything breaks"
        mm = matrix.CSVActionMatrix(SPRAY_ROOT + '/doc/tests/System Event-Action matrix - Matrix.csv')
        mm.update()
        ass = client.Assembler(mm, '', {})
        for eid in mm.get_event_ids():
            tokens = ass.get_event_field_tokens(eid)
            assert tokens

# That's enough for now.. .we'll go over to our application to run through all the
# callbacks. But lets test the integrated Assembler results...

    def test_assembler_integration(self):
        mm = matrix.CSVActionMatrix(SPRAY_ROOT + '/doc/tests/System Event-Action matrix - Matrix.csv')
        mm.update()
        ass = client.Assembler(mm, 'crafter.message.sent', {})
        ret = ass.assemble()
        self.assertEqual(ass.results, {'unfilled': set(['follower_email_address',
          'username', 'crafter_email', 'project_name', 'sponsor_email_address',
          'sponsor_first_name', 'copy admins_email_address', 'follower_first_name',
          'message']), 'results': {}, 'no_source': set([])})
        pass


