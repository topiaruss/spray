from spray import hub
from spray import interface
from spray import output
from spray.utils import observer
from zope.interface import implements
import datetime
import logging
import threading
import time

LOG = logging.getLogger(__name__)

# used for instantiating the correct matrix type based on live or testing
# configurations
ACTIONS = {}
AVAILABLE_ACTIONS = {}


def __action_log_listener(e):
    kwargs = e.__dict__
    klass, tick = kwargs.pop('klass', None), kwargs.pop('tick', None)
    ss = 'impl class: %s, step: %s, data: %s.' % (klass, tick, kwargs)
    LOG.info(ss)

# This is a long-lived broadcaster, to which anyone can subscribe. It has a
# longer lifetime than the actions that use it
BROADCASTER = observer.Observable()
BROADCASTER.subscribe(__action_log_listener)


class Action(observer.Observable):

    implements(interface.IAction)

    action_type = None

    def __init__(self, **kwargs):
        super(Action, self).__init__(**kwargs)

        #these are mandatory kwargs params
        self.event = kwargs['event']
        self.row = kwargs['row']

        #internal setup
        self.data = self.event.data
        self.setup_channel(self.row)

    def setup_channel(self, channel):
        pass

    @classmethod
    def register(cls):
        assert cls.action_type is not None
        AVAILABLE_ACTIONS[cls.action_type] = cls

    def handle(self):
        raise NotImplementedError

    def notify(self, tick, **kwargs):
        "notify listeners of processing steps"
        kwargs['klass'] = self.__class__.__name__
        kwargs['tick'] = tick
        BROADCASTER.notify(**kwargs)


class DummyEmailAction(Action):

    action_type = 'DummyEmailAction'

    def __init__(self, **kwargs):
        super(DummyEmailAction, self).__init__(**kwargs)

    def handle(self):
        self.notify('start-handle')
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        selection = {}
        for k in ('action_type', 'event_id', 'recipient'):
            selection[k] = self.row[k]
        pp.pprint(selection)
        pp.pprint(self.data)
        self.notify('end-handle')


DummyEmailAction.register()


class DummySMSAction(Action):

    action_type = 'DummySMSAction'

    def __init__(self, **kwargs):
        super(DummySMSAction, self).__init__(**kwargs)

    def _dump(self):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        selection = {}
        for k in ('action_type', 'event_id', 'recipient'):
            selection[k] = self.row[k]
        pp.pprint(selection)
        pp.pprint(self.data)

    def handle(self):
        self.notify('start-handle')
        #self._dump()
        self.notify('end-handle')


DummySMSAction.register()


class EmailAction(Action):

    action_type = 'EmailAction'

    def __init__(self, **kwargs):
        super(EmailAction, self).__init__(**kwargs)

    def setup_channel(self, row):
        # TODO: take the channel from the matrix, so we can switch test/prod
        self.channel = output.CHAN_REG.lookup('email')

    def handle(self):
        self.notify('handle')
        try:
            self.dest = self.channel.send(self.row, self.data)
        except Exception as e:
            import traceback
            tb = traceback.format_exc(8)  # 8 lines
            self.notify('handler-exception', exception=e,
              event=self.event, data=self.data, traceback=tb)
        self.notify('handle-end', data=self.data)
        # returning the outcome of the action. Used for testing
        return self


EmailAction.register()


class Processor(object):
    """
    Pulls events from its queue, looks them up, handles them.
    """

    def __init__(self, queue, matrix, running=True, max_time=None):
        if isinstance(queue, str):
            our_hub = hub.Hub()
            self.queue = our_hub.get_or_create(queue)
        else:
            self.queue = queue
        self.matrix = matrix
        self.expire = max_time and (datetime.datetime.now() + max_time) or None
        self.tt = threading.Thread(target=self.runner)
        if running:
            self.start()

    def runner(self):
        if self.expire is not None:
            print "running %s" % \
              ((self.expire and ("'til %s" % self.expire)) or '...')
        while self.is_alive:
            self.step()
            if self.expire is not None and datetime.datetime.now() > self.expire:
                self.is_alive = False

    def step(self):
        event = self.queue.get_event()
        if event is None:
            time.sleep(2)
            return
        self.notify('event-got')
        try:
            actions = self.matrix.get_actions(event)
            self.entrails = [a.handle() for a in actions]
        except Exception as e:
            self.notify('event-exception', exception=e, event=event)
        finally:
            event.delete()
            self.notify('event-deleted')
        self.notify('event-processed')

    def stop(self):
        if self.tt.is_alive():
            self.is_alive = False
            if self.queue.name == 'sprayui':
                self.queue.put(None)
            self.tt.join()

    def start(self):
        self.is_alive = True
        self.tt.start()

    def notify(self, tick, **kwargs):
        "notify listeners of processing steps"
        kwargs['klass'] = self.__class__.__name__
        kwargs['tick'] = tick
        BROADCASTER.notify(**kwargs)

ACTIONS['email'] = AVAILABLE_ACTIONS['EmailAction']
ACTIONS['SMS'] = AVAILABLE_ACTIONS['DummySMSAction']
