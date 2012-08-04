# Classic GOF Observer pattern

class ObsEvent(object):
    pass


class Observable(object):

    def __init__(self):
        # If you think the super() line is not needed, please get wise.
        # https://fuhm.net/super-harmful/
        super(Observable, self).__init__()
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
