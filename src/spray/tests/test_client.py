import jinja2
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
        self.assertRaises(jinja2.TemplateSyntaxError, ass.get_undef_body_fields, "{{intentionally broken}")

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
        mm = matrix.CSVActionMatrix(SPRAY_ROOT +
          '/doc/tests/System Event-Action matrix - Matrix.csv')
        mm.update()
        ass = client.Assembler(mm, 'crafter.message.sent', {})
        ret = ass.assemble()
        ret = ret  # trick lint
        self.assertEqual(ass.results, {'unfilled':
          set(['follower_email_address', 'username', 'crafter_email',
          'project_name', 'sponsor_email_address', 'sponsor_first_name',
          'copy admins_email_address', 'follower_first_name',
          'message']), 'results': {}, 'no_source': set([])})
        pass

    def test_late_recipient_expansion_no_context(self):
        mm = matrix.CSVActionMatrix(SPRAY_ROOT + '/doc/tests/System Event-Action matrix - Matrix.csv')
        mm.update()
        ass = client.Assembler(mm, 'sponsor.project.fundingtarget', {})
        ret = ass.assemble()
        ret = ret  # trick lint
        self.maxDiff = None
        self.assertEqual(ass.results,
          {'unfilled': set(['follower_first_name', 'project_name',
          'crafter_first_name', '_tweet_address', 'crafter_email_address',
          'crafter_SMS_address', '_facebook post_address',
          'crafter_last_name',
          'project__followers_email_address',
          'project__sponsors_email_address',
          'sponsor_first_name',
          'crafter_twitter_tag', 'project_url', 'days_until_completion_date',
          'crafter_facebook post_address', 'institution']),
          'results': {},
          'no_source': set([])} )
        pass

    # See other tests up at the project level, where we have users
    # and projects in context, and callbacks to fill the blanks.
