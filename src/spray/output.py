from boto import ses
from jinja2 import Environment
from spray import emailproc
from spray import interface
from spray import templating
from spray.settings import CREDENTIALS_FILENAME
from spray.utils import aws_credentials
from spray.utils import genfind
from spray.utils import genopen
from zope.interface import implements
import boto
import logging
import os
import smtplib

LOG = logging.getLogger(__name__)

# TODO: retrofit a zope interface for Channel hierarchy and unify formal params

# To setup custom filters, we need to establish an environment
env = Environment()

# Add the custom filters
env.filters['urlformat'] = templating.urlformat
env.filters['buttonformat'] = templating.buttonformat

# == Template registries == #
AVAILABLE_TEMPLATE_REGISTRIES = {}


class SimpleTemplateRegistry(object):

    def __init__(self, **kw):
        super(SimpleTemplateRegistry, self).__init__()
        self.reg = {}

    def _process_and_store(self, style, text):
        template = env.from_string(text)
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
        try:
            template = self.lookup(style)
        except KeyError:
            LOG.exception("missing template. Fallback to default")
            template = self.lookup('')
        return template.render(data)


class FSBasedTemplateRegistry(SimpleTemplateRegistry):
    """Any kind of file in the template directory will be included.
    bz2 and tgz files will be decompresses before processing.
    The filename up to the first '.' will be used as the style
    default.html will be registered as the default file. It will be registered
    under the name '' (an empty string).
    """

    def __init__(self, **kw):
        super(FSBasedTemplateRegistry, self).__init__(**kw)
        try:
            self.dirpath = kw['templates_dir']
        except KeyError as e:
            import sys
            raise type(e), type(e)("Missing parameter to Constructor %s" % e),\
               sys.exc_info()[2]
        assert os.path.isdir(self.dirpath)
        self.update()

    def update(self):
        templ_names = genfind.gen_find('*', self.dirpath)
        templ_files = genopen.gen_open(templ_names)
        for f in templ_files:
            style = os.path.basename(f.name).split('.')[0]
            if style == 'default':
                style = ''
            self._process_and_store(style, f.read())


DEFAULT_TEMPLATE_REGISTRY = SimpleTemplateRegistry()
SimpleTemplateRegistry.make_available('semail')
FSBasedTemplateRegistry.make_available('email',
  templates_dir='./templates/email')


# == Destination registries == #

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
        sender = data.get('from')
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

    def __init__(self, overrides=None):
        self.region = 'eu-west-1'
        self.overrides = overrides
        conf = aws_credentials.get_credentials(CREDENTIALS_FILENAME)
        region = ses.get_region(self.region)
        self.conn = boto.connect_ses(aws_access_key_id=conf[0],
          aws_secret_access_key=conf[1],
          region=region)

    def send(self, body, data):
        sender = data.get('from') or emailproc.TEMP_FROM_ADDRESS
        or_to = self.overrides and self.overrides['to_addresses'] or ''
        recipients = or_to or data['to']
        subject = data.get('subject') or data.get('subject_en_uk')
        assert type(sender) == type("")
        assert type(recipients) in (list, tuple)
        self.conn.send_email(sender, subject, body, recipients)

    def mpart_send(self, **kw):
        if self.overrides:
            hdr = """
            [[  ** JUST FOR DEBUG **
            Some of the original addresses were overridden. Original values:
            to: %s
            cc: %s
            bcc: %s
            Original Text message starts on the next line]]
            %s""" % (kw.get('to_addresses', ''),
              kw.get('cc_addresses', ''),
              kw.get('bcc_addresses', ''),
              kw.get('text_body', ''))
            kw['text_body'] = hdr
        kw.update(self.overrides or {})
        self.conn.send_email(**kw)

AmazonSESDestination.register()


# == Channels == #


class Channel(object):
    """
    Channel binds a template to a destination and does
    specific processing for a medium.  It's a place for adapter
    code that compensates for differences in destination types and
    params.
    medium: could be email, or sms - A chan therefore knows its own
    limitations.
    tempreg: is the template registry
    destination: is the implementation class, like smtp or SENDGRID
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

    def send(self, row, data, style=''):
        body = self.render(data, style)
        # temp kludge - I don't want the row going into the destination...
        data['subject_en_uk'] = row.get('subject_en_uk')
        self.dest.send(body, data)


class HTMLEmailChannel(Channel):
    """
    Formats the content of the message using the row's template,
    if it can find one. Then it uses the delivery template to wrap the
    message. Finally it does a stoneage html pass, to check the message
    is legal for email.
    It uses the mpart_send method of dest. Easiest route to MIME.
    """

    def __init__(self, **kw):
        super(HTMLEmailChannel, self).__init__(**kw)

    def render(self, row, data, style=''):
        send_params = emailproc.build_multipart_mail(env, row, data, self.tempreg)
        return send_params

    def send(self, row, data, style=''):
        #TODO: roll this into parent class - unify params
        send_params = self.render(row, data, style)
        self.dest.mpart_send(**send_params)


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
# in the meantime, sprayd.py switches the destination to AmazonSESDestination
email_channel = Channel(medium='email',
                        destination=DESTINATION_REGISTRY['DummyDestination']())
CHAN_REG.register(email_channel)

# TEST

DEFAULT_TEMPLATE_REGISTRY.register('', 'Hello {{ name }}!')
