from zope.interface import Attribute
from zope.interface import Interface


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


class IDestination(Interface):
    """A destination object can wrap message output systems"""

    destination_type = Attribute("""Type of the destination""")

    def send(message):
        """Send message to this destination"""
