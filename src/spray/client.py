from spray import hub


class Source(object):
    """Represents ...
    """
    def __init__(self, name, send_queue=None):
        assert type(name) == str
        self.name = name

        if send_queue is None:
            self.send_queue = hub.get_or_create(name)
        elif instance(send_queue, str):
            self.send_queue = hub.get_or_create(send_queue)
        else:
            self.send_queue = send_queue

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode("utf-8")

    def send(self, event_id, data=None):
        """Sends the event with passed event_id and data to the queue.
        """
        assert type(event_id) == str
        assert type(data) == dict

        self.send_queue.inject_event(event_id, data)
