import gspread
import os
from spray.utils import ucsv as csv

MATRICES = {}


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
                #if index == 0:
                #    continue
                rdict[titles[index]] = val
            lst = data.setdefault(eventid, [])
            lst.append(rdict)
        self.data = data

    def get_rows(self, event):
        raise NotImplementedError

    def get_actions(self, event):
        # late import to reduce dependencies for use of this module in client
        from spray import action
        ACTIONS = action.ACTIONS
        actionrows = self.data[event.event_id]
        return [ACTIONS[row['action type']](event=event, row=row) \
          for row in actionrows]

    def get_rows_for_event(self, eid=None):
        # returns a couple of rows for one event, or all rows
        if eid is not None:
            return self.data[eid]
        rows = []
        for k, v in self.data.items():
            rows.extend(v)
        return rows

    @classmethod
    def register(klass):
        MATRICES[klass.__name__] = klass


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
