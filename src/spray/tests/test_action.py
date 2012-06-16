import string
import sys
import unittest

from spray import action
from spray import event
from spray import interface
from spray import testing
from zope.interface import providedBy
from StringIO import StringIO


class TestAction(unittest.TestCase):

    def test_Action_conforms_to_interface(self):
        ee = event.Event('e')
        aa = action.Action(ee)
        assert interface.IAction in providedBy(aa)


class TestDummyEmailAction(unittest.TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        sys.stdout = self.held

    def test_DummyEmailAction_conforms_to_interface(self):
        ee = event.Event('e')
        aa = action.DummyEmailAction(ee)
        assert interface.IAction in providedBy(aa)

    def test_handle(self):
        ee = event.Event('e')
        aa = action.DummyEmailAction(ee)
        aa.handle()
        self.assertEqual(sys.stdout.getvalue(),
            "action: email, data: {'email': 'russf@topia.com',"
            "'name': 'Russ Ferriday'}")

    def test_action_type(self):
        pass

if __name__ == '__main__':
    unittest.main()
