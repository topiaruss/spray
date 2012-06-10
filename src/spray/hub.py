import Queue
from spray import event

QUEUES = {}

class HQueue(Queue.Queue):

    def __init__(self, name):
        Queue.Queue.__init__(self)
        self.name = name

    def putEvent(self, event):
        self.put(event)

    def getEvent(self):
        return self.get()

def get_or_create(name):
    return QUEUES.setdefault(name, HQueue(name))
