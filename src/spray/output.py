from jinja2 import Template
from spray import interface
from spray.utils import awsconfig
from zope.interface import implements
import boto
from boto import ses
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
        template = self.lookup(style)
        return template.render(data)


class Destination(object):

    implements(interface.IDestination)

    def _format_message(self, sender, recipients, body, headers={}):
        head = "From: %s\n" % sender
        key = "To:"
        for rr in recipients:
            head = head + "%s %s\n" % (key, rr)
            key = ""
        for k, v in headers:
            head = head + "%s: %s\n" % (k, v)
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
        headers = data.get('headers', {})
        assert type(sender) == str
        assert type(recipients) == list
        assert type(headers) == dict
        smtpd = smtplib.SMTP()
        smtpd.connect('localhost', 9025)
        message = self._format_message(sender, recipients, body, headers)
        smtpd.sendmail(sender, recipients, message)


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
        body = self.tempreg.render(data, style)
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


