class TemplateRegistry(dict):
    pass

class Channel(object):

    def __init__(self, medium, tempreg):
        self.medium = medium

class ChannelRegistry(object):

    reg = {}

    def lookup(self, medium):
        return self.reg[medium]

    def register(self, channel):
        medium = channel.medium
        self.reg[medium] = channel

    def send(self, medium, data, style=''):
        raise NotImplementedError


CHAN_REG = ChannelRegistry()


