import gspread
import os
import threading
from spray import hub
from spray import interface
from spray.utils import ucsv as csv
from zope.interface import implements


class Credentials(object):
    """
    Holds credentials.
    If not provided as parameters, name and password
    will be fished out of the credentials file
    """

    def __init__(self, email=None, password=None):
        if email is None:
            try:
                ff = open('credentials.txt', 'r')
            except IOError:
                home = os.getenv('USERPROFILE') or os.getenv('HOME')
                home_cred = os.path.join(home, '.spray.credentials.txt')
                try:
                    ff = open(home_cred, 'r')
                except IOError:
                    raise IOError('you need a creds file here %s' % home_cred)
            lines = ff.readlines()
            lines = [l.strip() for l in lines]
            self.email, self.password = lines[0], lines[1]
            return
        self.email, self.password = email, password


class ActionMatrix(object):
    """
    the abstract superclass to the ActionMatrix implementations,
    providing the update mechanism and booby-trapped
    placeholder methods.
    """

    def update(self):
        rows = self.get_rows()
        # titles has the col name by col index
        titles = {}
        for index, key in enumerate(rows[0]):
            titles[index] = key
        # data holds dicts of values by column title
        data = {}
        for row in rows[1:]:
            eventid = row[0]
            rdict = {}
            for index, val in enumerate(row):
                if index == 0:
                    continue
                rdict[titles[index]] = val
            lst = data.setdefault(eventid, [])
            lst.append(rdict)
        self.data = data

    def get_rows(self, event):
        raise NotImplementedError

    def get_actions(self, event):
        actionrows = self.data[event.event_id]
        return [ACTIONS[row['action type']](event, row) for row in actionrows]

    @classmethod
    def register(klass):
        MATRICES[klass.__name__] = klass

# used for instantiating the correct matrix type based on live or testing
# configurations
MATRICES = {}


class CSVActionMatrix(ActionMatrix):
    """
    This takes a CSV file made from the matrix tab of the
    Google example spreadsheet.
    """

    def __init__(self, filepath):
        self.filepath = filepath

    def get_rows(self):
        self.csvfile = open(self.filepath, 'r')
        rdr = csv.reader(self.csvfile)
        rows = [r for r in rdr]
        return rows

CSVActionMatrix.register()


class GoogleActionMatrix(ActionMatrix):

    def __init__(self, credentials, url):
        self.creds = credentials
        self.url = url

    def get_rows(self):
        gc = gspread.login(self.creds.email, self.creds.password)
        ss = gc.open_by_url(self.url)
        ws = ss.get_worksheet(1)
        return ws.get_all_values()

GoogleActionMatrix.register()


def matrixFactory(name, kwargs={}):
    "Instantiate a class instance, and provide note in case of param err."
    try:
        return MATRICES[name](**kwargs)
    except TypeError as exc:
        print exc
        print "***  Check __init__ params of %s ***" % name
        raise


ACTIONS = {}


class Action(object):

    implements(interface.IAction)

    action_type = None

    def __init__(self, event, row):
        self.event = event
        self.row = row

    @classmethod
    def register(cls):
        ACTIONS[cls.action_type] = cls

    def handle(self):
        raise NotImplementedError


class DummyEmailAction(Action):

    action_type = 'email'

    def handle(self):
        print 'action: %s, data: %s.' %\
            (self.action_type, self.event.data)
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.row)


DummyEmailAction.register()


class Processor(object):
    """
    Pulls events from its queue, looks them up, handles them.
    """

    def __init__(self, queue, matrix, running=True):
        if isinstance(queue, str):
            our_hub = hub.Hub()
            self.queue = our_hub.get_or_create(queue)
        else:
            self.queue = queue
        self.matrix = matrix
        self.tt = threading.Thread(target=self.runner)
        if running:
            self.start()

    def runner(self):
        while self.is_alive:
            self.step()

    def step(self):
        event = self.queue.get_event()
        actions = self.matrix.get_actions(event)
        [a.handle() for a in actions]
        print 'processed step'

    def stop(self):
        if self.tt.is_alive():
            self.is_alive = False
            self.tt.join()

    def start(self):
        self.is_alive = True
        self.tt.start()

