import unittest

from spray import action
from spray import event
from spray import interface
from spray import testing
from zope.interface import providedBy


class TestAction(unittest.TestCase):

    def test_Action_conforms_to_interface(self):
        ee = event.Event('e')
        aa = action.Action(ee)
        assert interface.IAction in providedBy(aa)
    
    def test_DummyEmailAction_conforms_to_interface(self):
        ee = event.Event('e')
        aa = action.DummyEmailAction(ee)
        assert interface.IAction in providedBy(aa)

    def test_action_type(self):
        pass


if __name__ == '__main__':
    unittest.main()
