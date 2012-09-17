from boto.sqs.connection import SQSConnection
from boto.sqs import regions
from spray import event
from spray import hub
from spray import interface
from spray.tests import TEST_CREDENTIALS_FILENAME
from spray.utils import aws_credentials
from time import sleep
from zope.interface import providedBy
import unittest


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
        assert ev.event_id == 'abc'

    def test_DummyQueue_event_factory_data(self):
        qq = hub.DummyQueue('send')
        ev = qq.event_factory('abc', dict(a=1))
        assert ev.data == {'a': 1}

    def test_DummyQueue_create_and_send(self):
        qq = hub.DummyQueue('send')
        qq.create_and_send('some.id')
        assert qq.get_event().event_id == 'some.id'

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

    qname = 'testx'
    delay = 0.5

    def setUp(self):
        # Ensure the queue is clear before we start, or we'll lose more hair
        creds = aws_credentials.get_credentials(
          TEST_CREDENTIALS_FILENAME)
        region_name = 'eu-west-1'
        region = [r for r in regions() if r.name == region_name][0]
        conn = SQSConnection(aws_access_key_id=creds[0],
          aws_secret_access_key=creds[1],
          region=region)
        q = conn.create_queue(self.qname, 30)
        cruft = q.get_messages(10)
        while cruft:
            for c in cruft:
                print 'deleting old message %s', c.__dict__
                q.delete_message(c)
            cruft = q.get_messages(10)

    def test_SQSQueue_conforms_to_interface(self):
        qq = hub.SQSQueue(self.qname)
        assert interface.IQueue in providedBy(qq)

    def test_SQSQueue_event_factory_name(self):
        qq = hub.SQSQueue(self.qname)
        ev = qq.event_factory('abc', dict(a=1))
        assert ev.event_id == 'abc'

    def test_SQSQueue_event_factory_data(self):
        qq = hub.SQSQueue(self.qname)
        ev = qq.event_factory('abc', dict(a=42))
        assert ev.data == {'a': 42}

    def test_SQSQueue_create_and_send(self):
        qq = hub.SQSQueue(self.qname)
        qq.create_and_send('silly.id')
        sleep(self.delay)
        ev = qq.get_event()
        ev.delete()
        assert ev.event_id == 'silly.id'

    def test_SQSQueue_check_return_type(self):
        qq = hub.SQSQueue(self.qname)
        qq.create_and_send('some.id')
        sleep(self.delay)
        ev = qq.get_event()
        ev.delete()
        assert ev.__class__.__name__ == 'SQSEvent'

    def test_SQSQueue_create_and_send_ordered_deleting(self):
        qq = hub.SQSQueue(self.qname)
        qq.create_and_send('some.id', data=dict(index=0))
        qq.create_and_send('some.id', data=dict(index=1))
        sleep(self.delay)
        evA = qq.get_event()
        evA.delete()
        evB = qq.get_event()
        evB.delete()
        # I'm using sets to accommodate weakly ordered responses
        indices = set([evA.data['index'], evB.data['index']])
        assert indices == set([0, 1])

