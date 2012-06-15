import unittest

from spray import hub
from spray import event
from spray import testing
from spray import interface
from zope.interface import providedBy


class TestQueue(unittest.TestCase):

    def test_DummyQueue_conforms_to_interface(self):
        qq = hub.DummyQueue('send')
        assert interface.IQueue in providedBy(qq)

    def test_DummyQueue_is_FIFO(self):
        ev1 = event.Event('ev1', {})
        ev2 = event.Event('ev2', {})
        qq = hub.DummyQueue('send')
        qq.put_event(ev1)
        qq.put_event(ev2)
        got = qq.get_event()
        assert got == ev1
        got = qq.get_event()
        assert got == ev2

    def test_DummyQueue_nowait(self):
        qq = hub.DummyQueue('send')
        try:
            _ = qq.get(False)
            _ == _ #fake out pyflakes
            # empty queue does not block, but throws Empty
            # so if we get here something is broken
            assert False
        except:
            pass

