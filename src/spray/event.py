from boto.sqs.message import Message
import base64
import msgpack

# TODO: Bring the events back into a proper hierarchy and
# conformant to a new zope interface 

class Event(object):

    def __init__(self, event_id, data={}):
        self.event_id = event_id
        self.data = data

    def __unicode__(self):
        return "<Event event_id %s, datakeys %s>" % \
            (self.event_id, self.data.keys())

    def __repr__(self):
        return "<Event %s:: event_id %s, datakeys %s>" % \
            (id(self), self.event_id, self.data.keys())
 
    def __str__(self):
        return unicode(self).encode('utf-8')


    def delete(self):
        pass


class SQSEventDecodeError(Exception):
    pass


class SQSEvent(Message):
    def __init__(self, queue=None, body=None, xml_attrs=None,
                 event_id='', data={},):
        if body == None or body == '':
            body = dict(event_id=event_id, data=data)
        Message.__init__(self, queue, body)

    def __unicode__(self):
        return "<SQSEvent event_id %s, datakeys %s>" % (self.event_id, self.data.keys())

    def __repr__(self):
        return "<SQSEvent %s:: event_id %s, datakeys %s>" % \
               (id(self), self.event_id, self.data.keys())

    def __str__(self):
        return unicode(self).encode('utf-8')


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
        ret = dict(event_id=self.event_id, data=self.data)
        return ret

    def set_body(self, value):
        try:
            self.event_id = value['event_id']
            self.data = value['data']
        except:
            import pdb; pdb.set_trace()
            pass

