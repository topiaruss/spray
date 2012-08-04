import unittest
from spray import action
from spray import event
from spray import interface
from zope.interface import providedBy


class TestAction(unittest.TestCase):

    def test_Action_conforms_to_interface(self):
        ee = event.Event('e')
        aa = action.Action(event=ee, row={})
        assert interface.IAction in providedBy(aa)


class TestDummyEmailAction(unittest.TestCase):

    def setUp(self):
        pass
        #import sys
        #from StringIO import StringIO
        #self.held, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        pass
        #sys.stdout = self.held

    def test_DummyEmailAction_conforms_to_interface(self):
        ee = event.Event('e')
        aa = action.DummyEmailAction(event=ee, row={})
        assert interface.IAction in providedBy(aa)

    def test_handle(self):
        ee = event.Event('e')
        aa = action.DummyEmailAction(event=ee, row={})
        # Just check the method is there
        assert aa.handle

    def test_action_type(self):
        ee = event.Event('e')
        aa = action.DummyEmailAction(event=ee, row={})
        assert aa.action_type == 'email'


if __name__ == '__main__':
    unittest.main()
