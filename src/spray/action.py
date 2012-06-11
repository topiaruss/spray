import gspread
import threading
from spray.utils import ucsv as csv


class Credentials(object):

    def __init__(self, email=None, password=None):
        if email is None:
            ff = open('credentials.txt', 'r')
            lines = ff.readlines()
            lines = [l.strip() for l in lines]
            self.email, self.password = lines[0], lines[1]
            return
        self.email, self.password = email, password


class ActionMatrix(object):

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
        raise NotImplementedError

class CSVActionMatrix(ActionMatrix):

    def __init__(self, filepath):
        self.csvfile = open(filepath, 'r')

    def get_rows(self):



    def get_actions(self, event):
        raise NotImplementedError



class GoogleActionMatrix(ActionMatrix):

    def __init__(self, credentials, url):
        self.creds = credentials
        self.url = url

    def get_rows(self):
        gc = gspread.login(self.creds.email, self.creds.password)
        ss = gc.open_by_url(self.url)
        ws = ss.get_worksheet(1)
        return ws.get_all_values()


    def get_actions(self, event):
        actionrows = self.data[event.name]
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

class DummyEmailAction(Action):

    action_type = 'email'

    def handle(self):
        print 'action: %s data: %s.' %\
            (self.action_type, self.event.data)

DummyEmailAction.register()


class Processor(object):

    def __init__(self, queue, matrix, running=True):
        self.tt=threading.Thread(target=self.runner)
        if running:
            self.start()

    def runner(self):
        while self.is_alive:
            self.step()

    def step(self):
        pass 

    def stop(self):
        self.is_alive = False
        self.thread.join()

    def start(self):
        raise NotImplementedError

