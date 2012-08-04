# Classic GOF Observer pattern

class ObsEvent(object):
    pass


class Observable(object):

    def __init__(self):
        self.observers = []

    def subscribe(self, observer):
        self.observers.append(observer)

    def notify(self, **attrs):
        e = ObsEvent()
        e.source = self
        for k, v in attrs.iteritems():
            setattr(e, k, v)
        for fn in self.observers:
            fn(e)
