from boto import ses
from jinja2 import Template
from spray import interface
from spray.utils import awsconfig
from zope.interface import implements
import boto
import os
import smtplib

AVAILABLE_TEMPLATE_REGISTRIES = {}

class SimpleTemplateRegistry(object):

    def __init__(self, **kw):
        super(SimpleTemplateRegistry, self).__init__()
        self.reg = {}

    def _process_and_store(self, style, text):
        template = Template(text)
        self.reg[style] = template

    @classmethod
    def make_available(cls, medium, **kwargs):
        AVAILABLE_TEMPLATE_REGISTRIES[medium] = cls(**kwargs)

    def register(self, style, text):
        "register a template in this registry"
        self._process_and_store(style, text)

    def lookup(self, style):
        """returns a processed jinja2 style Template ready for render()"""
        return self.reg[style]

    def render(self, data, style=''):
        """convenience method that does the lookup and render in one step"""
        template = self.lookup(style)
        return template.render(data)

class FSBasedTemplateRegistry(SimpleTemplateRegistry):

    def __init__(self, **kw):
        super(FSBasedTemplateRegistry, self).__init__(**kw)
        try:
            self.dirpath = kw['templates_dir']
        except KeyError as e:
            import sys
            raise type(e), type(e)("Missing parameter to Constructor %s" % e), sys.exc_info()[2]

        assert os.path.isdir(self.dirpath)



DEFAULT_TEMPLATE_REGISTRY = SimpleTemplateRegistry()
SimpleTemplateRegistry.make_available('email')
FSBasedTemplateRegistry.make_available('hemail', templates_dir='./templates/email')

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
    """ Channel binds a template to a destination and does
    specific processing for a medium.
    medium could be email, or sms - it knows therefore about channel
    limitations.
    tempreg is the template registry
    destination is the implementation class, like smtp or SENDGRID
    """

    def __init__(self, **kw):
        # Some don't think this line is necessary. It is.
        super(Channel, self).__init__()

        # Note, these are mandatory - no default values
        self.medium = kw['medium']
        self.dest = kw['destination']

        # optional - defaults to None
        self.tempreg = kw.get('tempreg', None)
        self.select_registry()

    def select_registry(self):
        "allow flexibility setting the reg, and default to same name as medium"
        # TODO : improve this line
        if isinstance(self.tempreg, SimpleTemplateRegistry):
            return  # That's OK - the caller set the registry explicitly
        regname = self.tempreg
        if self.tempreg in (None, ''):
            regname = self.medium
        self.tempreg = AVAILABLE_TEMPLATE_REGISTRIES[regname]

    def render(self, data, style=''):
        return self.tempreg.render(data, style)

    def send(self, data, style=''):
        body = self.render(data, style)
        self.dest.send(body, data)

class HTMLEmailChannel(Channel):
    """
    Formats the content of the message using the row's template,
    if it can find one. Then it uses the delivery template to wrap the
    message. Finally it does a stoneage html pass, to check the message
    is legal for email.
    """

    def __init__(self, **kw):
        super(HTMLEmailChannel, self).__init__(**kw)

    def render(self, data, style=''):
        # first expand the content of the message using the template
        # from the row.

        # Now render the body into the framework template
        return self.tempreg.render(data, style)


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
email_channel = Channel(medium='email',  # tempreg=DEFAULT_TEMPLATE_REGISTRY,
                        destination=DESTINATION_REGISTRY['DummyDestination']())
CHAN_REG.register(email_channel)

# TEST

DEFAULT_TEMPLATE_REGISTRY.register('', 'Hello {{ name }}!')
