from jinja2 import Template
from spray import interface
from spray.utils import awsconfig
from zope.interface import implements
import boto
from boto import ses
import smtplib


class TemplateRegistry(object):

    reg = {}

    def _process_and_store(self, style, text):
        template = Template(text)
        self.reg[style] = template

    def register(self, style, text):
        self._process_and_store(style, text)

    def lookup(self, style):
        """returns a processed jinja2 style Template ready for render()"""
        return self.reg[style]

    def render(self, data, style=''):
        """convenience method that does the lookup and render in one step"""
        template = self.lookup(style)
        return template.render(data)

DEFAULT_TEMPLATE_REGISTRY = TemplateRegistry()

DESTINATION_REGISTRY = {}


class Destination(object):

    implements(interface.IDestination)

    def _format_message(self, sender, recipients, body, headers={}):
        head = "From: %s\n" % sender
        key = "To:"
        for rr in recipients:
            head = head + "%s %s\n" % (key, rr)
            key = ""
        for k, v in sorted(headers.items()):
            head = head + "%s: %s\n" % (k, v)
        head = head + "\n"
        return head + body

    def send(self, body, data):
        return NotImplementedError

    @classmethod
    def register(klass):
        DESTINATION_REGISTRY[klass.__name__] = klass


class DummyDestination(Destination):

    implements(interface.IDestination)

    def send(self, body, data):
        print body

DummyDestination.register()


class MockSmtpDestination(Destination):

    implements(interface.IDestination)

    def __init__(self, host, port):
        self.host, self.port = host, port

    def send(self, body, data):
        sender = data['from']
        recipients = data['to']
        headers = data.get('headers', {})
        assert type(sender) == str
        assert type(recipients) == list
        assert type(headers) == dict
        smtpd = smtplib.SMTP()
        smtpd.connect('localhost', 9025)
        message = self._format_message(sender, recipients, body, headers)
        smtpd.sendmail(sender, recipients, message)

MockSmtpDestination.register()


class AmazonSESDestination(Destination):

    implements(interface.IDestination)

    def __init__(self):
        self.region = 'eu-west-1'
        conf = awsconfig.get_aws_config()
        region = ses.get_region(self.region)
        self.conn = boto.connect_ses(aws_access_key_id=conf[0],
          aws_secret_access_key=conf[1],
          region=region)

    def send(self, body, data):
        sender = data['from']
        recipients = data['to']
        subject = data['subject']
        assert type(sender) == type("")
        assert type(recipients) == type([])
        self.conn.send_email(sender, subject, body, recipients)

AmazonSESDestination.register()


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
        # This render expands the core of the body
        body = self.tempreg.render(data, style)
        # The destination may expand the content further
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

# TODO: replace hardwired channels with sprayd.cfg channels
email_channel = Channel('email', dict(foo=1), #DEFAULT_TEMPLATE_REGISTRY,
                        DESTINATION_REGISTRY['DummyDestination']())
CHAN_REG.register(email_channel)
