from zope.interface import Interface
from zope.interface import Attribute

class IQueue(Interface):
    """A queue object"""

    name = Attribute("""Name of the queue""")

    def put_event(event_in):
        """queue an event"""

    def get_event(block=True, timeout=None):
        """remove and return the oldest event from the queue"""

    def event_factory(event_id, data={}):
        """return an event of the right type for this queue"""

    def create_and_send(event_id, data={}):
        """create the type of event for this queue and send it"""

class IAction(Interface):
    """An action object"""

    action_type = Attribute("""Type of the action""")

    def register():
        """Register this action"""

    def handle():
        """Handle the event"""
