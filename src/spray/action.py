import gspread


class Credentials(object):

    def __init__(self, email=None, password=None):
        if email is None:
            ff = open('credentials.txt', 'r')
            lines = ff.readlines()
            lines = [l.strip() for l in lines]
            self.email, self.password = lines[0], lines[1]
            return
        self.email, self.password = email, password


class GoogleActionMatrix(object):

    def __init__(self, credentials, url):
        self.creds = credentials

    def update(self):
        gc = gspread.login(self.creds.email, self.creds.password)
        url = 'https://docs.google.com/a/sponsorcraft.com/' \
            'spreadsheet/ccc?key=' \
            '0AgfJ64xPw-46dENnMWQwM2dOTTNaZWo3M1JZOEtVa1E'
        ss = gc.open_by_url(url)
        ws = ss.get_worksheet(1)
        rows = ws.get_all_values()
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

    def get_actions(self, event):
        actionrows = self.data[event.name]
        import pdb; pdb.set_trace()
        return [ACTIONS[e['action type']](event) for e in actionrows]

ACTIONS = {}

class Action(object):

    action_type = None

    def __init__(self, event):
        self.event = event

    @classmethod
    def register(cls):
        ACTIONS[cls.action_type] = cls

    def handle(self):
        raise NotImplementedError

class EmailAction(Action):

    action_type = 'email'

    def handle(self):
        print self.action_type, self.event.data

EmailAction.register()
