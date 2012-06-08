from spray import event


class Queue(object):
    def __init__(self, name):
        self.name = name
        self._queue = []

    def append(self, event):
        self._queue.append(event)

    def inject_event(self, event_id, data):
        assert type(event_id) == str
        assert type(data) == dict

        e = event.Event(event_id, data)
        self._queue.append(e)

    def get_next(self):
        return self._queue[0]


def get_or_create(name):
    return Queue(name)
