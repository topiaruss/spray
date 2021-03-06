from boto.sqs import regions
from boto.sqs.connection import SQSConnection
from spray import event
from spray import interface
from spray.utils import aws_credentials
from zope.interface import implements
import Queue
import decimal


# The singleton directory of ...
QUEUES = {}


class DummyQueue(Queue.Queue):
    """
    A dummy queue used for function and doc testing
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
            acc_sec_pair = aws_credentials.get_credentials()
        self.region_name = 'eu-west-1'
        self.region = [r for r in regions() if r.name == self.region_name][0]
        self.conn = SQSConnection(aws_access_key_id=acc_sec_pair[0],
          aws_secret_access_key=acc_sec_pair[1],
          region=self.region)
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

    def _expand_decimal_values(self, data):
        """expand Decimals which otherwise cause msgpack exception"""
        for k,v in  data.items():
            if type(v) is decimal.Decimal:
                data[k] = unicode(v)

    def create_and_send(self, event_id, data={}):
        self._expand_decimal_values(data)
        ev = self.event_factory(event_id=event_id, data=data)
        self.put_event(ev)

QUEUES['test'] = DummyQueue('test')
QUEUES['send'] = DummyQueue('send')
QUEUES['sprayui'] = DummyQueue('sprayui')
QUEUES['testSQS'] = SQSQueue('testSQS')
QUEUES['testSQS-2'] = SQSQueue('testSQS-2')
QUEUES['testSQS-3'] = SQSQueue('testSQS-3')
QUEUES['mainSQS'] = SQSQueue('mainSQS')
QUEUES['spray-preview'] = SQSQueue('spray-preview')


class Hub(object):
    def get_or_create(self, name):
        """Utility to grab or create a named queue"""
        return QUEUES.setdefault(name, DummyQueue(name))

HUB = Hub()
