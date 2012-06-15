import Queue
from spray import interface
from spray import event as event
from zope.interface import implements

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


def get_or_create(name):
    """Utility to grab or create a named queue"""
    return QUEUES.setdefault(name, DummyQueue(name))
