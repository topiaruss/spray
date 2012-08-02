from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from spray import event
from spray import interface
from spray.utils import awsconfig
from zope.interface import implements
import base64
import msgpack
import Queue

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


class SQSEventxx(Message):

    def __init__(self, event_id, data={}, queue=None):
        self.name = event_id
        self.data = data
        self._body = self.name

    # def __unicode__(self):
    #     return "<Event %s, datakeys %s>" % (self.name, self.data.keys())

    # def __repr__(self):
    #     return "<Event %s:: %s, datakeys %s>" % \
    #            (id(self), self.name, self.data.keys())

    # def __str__(self):
    #     return unicode(self).encode('utf-8')


class SQSEventDecodeError(Exception):
    pass


class SQSEvent(Message):
    """
    """

    def __init__(self, queue=None, body=None, xml_attrs=None, event_id='',
                 data={}):
        if body == None or body == '':
            body = dict(name=event_id, data=data)
        Message.__init__(self, queue, body)

    def decode(self, value):
        # takes an encoded dict, returns that dict decoded.
        try:
            value = base64.b64decode(value)
            value = msgpack.loads(value)
        except:
            import traceback
            traceback.print_exc()
            raise SQSEventDecodeError('Unable to decode message', self)
        return value

    def encode(self, value):
        # takes a dict with all attrs inside it
        packed = msgpack.dumps(value)
        return base64.b64encode(packed)

    def get_body(self):
        ret = dict(name=self.name, data=self.data)
        return ret

    def set_body(self, value):
        try:
            self.name = value['name']
            self.data = value['data']
        except:
            import pdb; pdb.set_trace()
            pass

class SQSQueue(object):

    implements(interface.IQueue)

    def __init__(self, name, acc_sec_pair=None, visibility_timeout=30):
        self.name = name
        if acc_sec_pair is None:
            acc_sec_pair = awsconfig.get_aws_config()
        self.conn = SQSConnection(*acc_sec_pair)
        self.q = self.conn.create_queue(name, visibility_timeout)
        self.q.set_message_class(SQSEvent)

    def put_event(self, event_in):
        assert isinstance(event_in, SQSEvent)
        self.q.write(event_in)

    def get_event(self, block=True, timeout=None):
        ev = self.q.read()
        return ev

    def event_factory(self, event_id, data={}):
        return SQSEvent(event_id=event_id, data=data)

    def create_and_send(self, event_id, data={}):
        ev = self.event_factory(event_id=event_id, data=data)
        self.put_event(ev)


class Hub(object):

    def get_or_create(self, name):
        """Utility to grab or create a named queue"""
        return QUEUES.setdefault(name, DummyQueue(name))

