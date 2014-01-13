import gspread
import os
from spray.utils import ucsv as csv
from django.contrib.sites.models import Site

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
    def __init__(self, *args, **kwargs):
        self.data = None
        self.provenance = u""

    def _ensure_updated(self):
        if self.data is None:
            raise UserWarning('Have you called ActionMatrix.upate()?')

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

    def get_event_ids(self):
        return self.data.keys()

    def get_actions(self, event):
        # late import to reduce dependencies for use of this module in client
        self._ensure_updated()
        from spray import action
        ACTIONS = action.ACTIONS
        actionrows = self.data[event.event_id]

        # Only keep actions that match our site name. TODO settle on either site_id or site_name
        event_site_name = Site.objects.get(id=event.data['site_id']).folder_name
        actionrows = [row for row in actionrows if row['site_name'] == event_site_name]

        return [ACTIONS[row['action_type']](event=event, row=row) for row in actionrows]

    def get_rows_for_event(self, event_id=None, site_id=None):
        "returns a couple of rows for one event, or all rows"
        self._ensure_updated()
        if event_id is not None:
            # this is a potentially multi-row response
            event_rows = self.data.get(event_id, [])
            site_name = Site.objects.get(id=site_id).folder_name
            site_event_rows = [row for row in event_rows if row['site_name'] == site_name]
            return site_event_rows
        # we must agglomerate the many multi-row sequences
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

    def __init__(self, filepath, *args, **kwargs):
        self.filepath = filepath
        self.provenance = "Pending CSV file at: %s" % self.filepath
        super(CSVActionMatrix, self).__init__(*args, **kwargs)

    def get_rows(self):
        self.csvfile = open(self.filepath, 'r')
        self.provenance = "CSV file at: %s" % self.filepath
        rdr = csv.reader(self.csvfile)
        rows = [r for r in rdr]
        return rows

CSVActionMatrix.register()


class GoogleActionMatrix(ActionMatrix):

    def __init__(self, credentials, url, *args, **kwargs):
        self.creds = credentials
        self.url = url
        self.provenance = "Pending Google SS at %s" % url
        super(GoogleActionMatrix, self).__init__(*args, **kwargs)

    def get_rows(self):
        gc = gspread.login(self.creds.email, self.creds.password)
        ss = gc.open_by_url(self.url)
        self.provenance = "Google SS at %s" % self.url
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
