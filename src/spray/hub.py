from spray import event
from spray import interface
from zope.interface import implements
import Queue
from spray.utils import awsconfig
from spray import interface
from zope.interface import implements
from boto.sqs.connection import SQSConnection


# The singleton directory of ...
QUEUES = {}


class DummyQueue(Queue.Queue):
    """
    A dummy queue used for function and doc testing
    TODO: class hierarchy or ZCA interface
    """
    implements(interface.IQueue)

    def __init__(self, name):
        # 'old' style class - can't use super()
        Queue.Queue.__init__(self)
        self.name = name

    def put_event(self, event_in):
        assert isinstance(event_in, event.Event)
        self.put(event_in)

    def get_event(self, block=True, timeout=None):
        return self.get()

    def event_factory(self, event_id, data={}):
        return event.Event(event_id, data)

    def create_and_send(self, event_id, data={}):
        ev = self.event_factory(event_id, data)
        self.put_event(ev)


class SQSQueue(object):

    implements(interface.IQueue)

    def __init__(self, name, acc_sec_pair=None, visibility_timeout=30):
        self.name = name
        if acc_sec_pair is None:
            acc_sec_pair = awsconfig.get_aws_config()
        self.conn = SQSConnection(*acc_sec_pair)
        self.q = self.conn.create_queue(name, visibility_timeout)
        self.q.set_message_class(event.SQSEvent)

    def put_event(self, event_in):
        assert isinstance(event_in, event.SQSEvent)
        self.q.write(event_in)

    def get_event(self, block=True, timeout=None):
        ev = self.q.read()
        return ev

    def event_factory(self, event_id, data={}):
        return event.SQSEvent(event_id=event_id, data=data)

    def create_and_send(self, event_id, data={}):
        ev = self.event_factory(event_id=event_id, data=data)
        self.put_event(ev)


class Hub(object):

    def get_or_create(self, name):
        """Utility to grab or create a named queue"""
        return QUEUES.setdefault(name, DummyQueue(name))

