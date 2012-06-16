from jinja2 import Template
from spray import interface
from zope.interface import implements


class TemplateRegistry(dict):

    def process_and_store(self, style, text):
        template = Template(text)
        self[style] = template

    def register(self, style, text):
        self.process_and_store(style, text)

    def lookup(self, style):
        """returns a jinja2 style Template ready for render()"""
        return self[style]

    def render(self, data, style=''):
        """convenience method that does the lookup and render in one step"""
        template = self[style]
        return template.render(**data)


class DummyDestination(object):

    implements(interface.IDestination)

    def send(self, message):
        print message


class Channel(object):

    def __init__(self, medium, tempreg, destination):
        self.medium = medium
        self.tempreg = tempreg
        self.dest = destination

    def send(self, data, style=''):
        self.dest.send(self.tempreg.render(data))


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


