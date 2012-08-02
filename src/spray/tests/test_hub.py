import unittest

from spray import hub
from spray import event
#from spray import testing
from spray import interface
from zope.interface import providedBy


class TestDummyQueue(unittest.TestCase):

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

    def test_DummyQueue_event_factory_name(self):
        qq = hub.DummyQueue('send')
        ev = qq.event_factory('abc', dict(a=1))
        assert ev.name == 'abc'

    def test_DummyQueue_event_factory_data(self):
        qq = hub.DummyQueue('send')
        ev = qq.event_factory('abc', dict(a=1))
        assert ev.data == {'a': 1}

    def test_DummyQueue_create_and_send(self):
        qq = hub.DummyQueue('send')
        qq.create_and_send('some.id')
        assert qq.get_event().name == 'some.id'

    def test_DummyQueue_nowait(self):
        qq = hub.DummyQueue('send')
        try:
            _ = qq.get(False)  # convention says that _ is throw-away
            _ == _  # fake out pyflakes

            # We told get on an empty queue not to block
            # When an empty queue does not block, it throws Empty
            # So if we get here something is broken
            assert False
        except:
            pass

class TestSQSQueue(unittest.TestCase):

    qname = 'test'

    def test_SQSQueue_conforms_to_interface(self):
        qq = hub.SQSQueue(self.qname)
        assert interface.IQueue in providedBy(qq)

    def test_SQSQueue_event_factory_name(self):
        qq = hub.SQSQueue(self.qname)
        ev = qq.event_factory('abc', dict(a=1))
        assert ev.name == 'abc'

    def test_SQSQueue_event_factory_data(self):
        qq = hub.SQSQueue(self.qname)
        ev = qq.event_factory('abc', dict(a=1))
        assert ev.data == {'a': 1}

    def test_SQSQueue_create_and_send(self):
        qq = hub.SQSQueue(self.qname)
        qq.create_and_send('some.id')
        assert qq.get_event().name == 'some.id'

    def test_SQSQueue_check_return_type(self):
        qq = hub.SQSQueue(self.qname)
        qq.create_and_send('some.id')
        ev = qq.get_event()
        import pdb; pdb.set_trace()
        assert type(ev) == hub.SQSEvent

