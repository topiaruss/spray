from zope.interface import Interface
from zope.interface import Attribute

class IQueue(Interface):
    """A queue object"""

    name = Attribute("""Name of the queue""")

    def put_event(self, event_in):
        """queue an event"""

    def get_event(self, block=True, timeout=None):
        """remove and return the oldest event from the queue"""
