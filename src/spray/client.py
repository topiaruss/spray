from spray import hub


class Source(object):
    """Represents ...
    """
    def __init__(self, name, send_queue=None):
        assert type(name) == str
        self.name = name
        our_hub = hub.Hub()
        if send_queue is None:
            # just create a queue named after the source
            self.send_queue = our_hub.get_or_create(name)
        elif isinstance(send_queue, str):
            # user wants us to make a queue with certain name
            self.send_queue = our_hub.get_or_create(send_queue)
        else:
            # use queue we were handed
            self.send_queue = send_queue

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode("utf-8")

    def send(self, event_id, data={}):
        """Sends the event with passed event_id and data to the queue.
        """
        assert type(event_id) == str
        assert type(data) == dict

        self.send_queue.create_and_send(event_id, data)
