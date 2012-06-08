class Event(object):

    def __init__(self, event_id, data={}):
        self.name = event_id
        self.data = data

    def __unicode__(self):
        return "<Event %s, datakeys %s>" % (self.name, self.data.keys())

    def __repr__(self):
        return "<Event %s:: %s, datakeys %s>" % (id(self), self.name, self.data.keys())
 
    def __str__(self):
        return unicode(self).encode('utf-8')

