from jinja2 import Template
from spray import interface
from zope.interface import implements
import smtplib


class TemplateRegistry(dict):

    def _process_and_store(self, style, text):
        template = Template(text)
        self[style] = template

    def register(self, style, text):
        self._process_and_store(style, text)

    def lookup(self, style):
        """returns a processed jinja2 style Template ready for render()"""
        return self[style]

    def render(self, data, style=''):
        """convenience method that does the lookup and render in one step"""
        template = self[style]
        return template.render(data)

class Destination(object):

    implements(interface.IDestination)

    def _format_message(self, sender, recipients, body, headers={}):
        head = "From: %s\n" % sender
        key = "To:"
        for rr in recipients:
            head = head + "%s %s\n" % (key, rr)
            key = ""
        for hh in headers:
            head = head + "%s: %s\n"
        head = head + "\n"
        return head + body

    def send(self, body, data):
        return NotImplementedError

class DummyDestination(object):

    implements(interface.IDestination)

    def send(self, body, data):
        print body

class MockSmtpDestination(Destination):

    implements(interface.IDestination)

    def __init__(self, host, port):
        self.host, self.port = host, port

    def send(self, body, data):
        sender = data['from']
        recipients = data['to']
        assert type(sender) == type("")
        assert type(recipients) == type([])
        smtpd = smtplib.SMTP()
        smtpd.connect('localhost', 9025)
        message = self._format_message(sender, recipients, body)
        smtpd.sendmail(sender, recipients, message)



class Channel(object):

    def __init__(self, medium, tempreg, destination):
        """ medium could be email.
        tempreg is the template registry
        destination is the implementation class, like smtp or gmail
        """

        self.medium = medium
        self.tempreg = tempreg
        self.dest = destination

    def send(self, data, style=''):
        body = self.tempreg.render(data)
        self.dest.send(body, data)


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


