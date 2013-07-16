from boto import ses
from collections import defaultdict
from spray import emailproc
from spray import interface
from spray import jinjaenv
from spray import SPRAY_ROOT
from spray.settings import CREDENTIALS_FILENAME
from spray.utils import aws_credentials
from spray.utils import genfind
from spray.utils import genopen
from zope.interface import implements
import boto
import logging
import os
import smtplib
import time

LOG = logging.getLogger(__name__)

# TODO: retrofit a zope interface for Channel hierarchy and unify formal params

env = jinjaenv.env
ptenv = jinjaenv.ptenv

# == Template registries == #
AVAILABLE_TEMPLATE_REGISTRIES = {}


class SimpleTemplateRegistry(object):
    "registry by site, with the default site being 'sponsorcraft_com'"
    # {site1: {style1: 'template blah'}}

    def __init__(self, **kw):
        super(SimpleTemplateRegistry, self).__init__()
        self.reg = defaultdict(dict)

    def _process_and_store(self, style, text, site='sponsorcraft_com'):
        template = env.from_string(text)
        self.reg[site][style] = template

    @classmethod
    def make_available(cls, medium, **kwargs):
        AVAILABLE_TEMPLATE_REGISTRIES[medium] = cls(**kwargs)

    def register(self, style, text, site='sponsorcraft_com'):
        "register a template in this registry"
        self._process_and_store(style, text, site)

    def lookup(self, style, site='sponsorcraft_com'):
        """returns a processed jinja2 style Template ready for render()"""
        return self.reg[site][style]

    def render(self, data, style='', site='sponsorcraft_com'):
        """convenience method that does the lookup and render in one step"""
        try:
            template = self.lookup(style, site)
        except KeyError:
            LOG.exception("missing template. Fallback to default")
            template = self.lookup('', site)
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
            # this is becoming the directory for sites, which then
            # contain the original templates, but the name does not change
            # in the settings file, so I'm not going to rename it.
            self.dirpath = kw['templates_dir']
        except KeyError as e:
            import sys
            raise type(e), type(e)("Missing parameter to Constructor %s" % e),\
               sys.exc_info()[2]
        assert os.path.isdir(self.dirpath)
        self.update()

    def update(self):
        names = [
            o for o in os.listdir(self.dirpath) if
            os.path.isdir(os.path.join(self.dirpath, o))]
        for site_name in names:
            site_path = os.path.join(self.dirpath, site_name)
            templ_names = genfind.gen_find('*', site_path)
            templ_files = genopen.gen_open(templ_names)
            for f in templ_files:
                style = os.path.basename(f.name).split('.')[0]
                if style == 'default':
                    style = ''
                self._process_and_store(style, f.read(), site=site_name)


DEFAULT_TEMPLATE_REGISTRY = SimpleTemplateRegistry()
SimpleTemplateRegistry.make_available('semail')
templ_dir = os.path.join(SPRAY_ROOT, 'templates')
FSBasedTemplateRegistry.make_available('email', templates_dir=templ_dir)


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


class  FakeSES(object ):

    def __init__(self):
        self.output = []

    def send_email(self, *args, **kwargs):
        self.output.append(dict(args=args, kwargs=kwargs))

    def get_traffic(self):
        out = self.output
        self.output = []
        return out


class AmazonSESDestination(Destination):

    implements(interface.IDestination)

    def __init__(self, overrides=None):
        self.overrides = overrides
        conf = aws_credentials.get_credentials(CREDENTIALS_FILENAME)
        region = ses.regions()[0]  # Getting first region
        self.conn = boto.connect_ses(aws_access_key_id=conf[0],
          aws_secret_access_key=conf[1],
          region=region)

    def send(self, body, data):
        sender = data.get('from') or emailproc.TEMP_FROM_ADDRESS
        or_to = self.overrides and self.overrides['to_addresses'] or ''
        recipients = or_to or data['to']
        subject = data.get('subject') or data.get('subject_en-gb')
        assert type(sender) == type("")
        assert type(recipients) in (list, tuple)
        self.conn.send_email(sender, subject, body, recipients)
        #naiive rate limit
        if not isinstance(self.conn, FakeSES):
            time.sleep(0.25)  # SES rate limit 5Hz

    def mpart_send(self, **kw):
        if self.overrides and any(self.overrides.values()):
            hdr = """
            [[  ** JUST FOR DEBUG **
            Some of the original addresses were overridden. Original values:
            to: %s
            cc: %s
            bcc: %s
            Original Text message starts after the blank line]]\n\n%s""" %\
              (kw.get('to_addresses', ''),
              kw.get('cc_addresses', ''),
              kw.get('bcc_addresses', ''),
              kw.get('text_body', ''))
            kw['text_body'] = hdr
            # override any, override all
            kw.update(self.overrides)
        self.conn.send_email(**kw)

    def get_traffic(self):
        return self.conn.get_traffic()

AmazonSESDestination.register()


class DummyAmazonSESDestination(AmazonSESDestination):

    implements(interface.IDestination)

    def __init__(self, overrides=None):
        self.overrides = overrides
        self.conn = FakeSES()

    def get_traffic(self):
        return self.conn.get_traffic()

DummyAmazonSESDestination.register()

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
        data['subject_en-gb'] = row.get('subject_en-gb')
        self.dest.send(body, data)


class HTMLEmailChannel(Channel):
    """
    Formats the content of the message using the row's template,
    if it can find one. Then it uses the delivery template to wrap the
    message.
    It uses the mpart_send method of dest. Easiest route to MIME.
    """

    def __init__(self, **kw):
        super(HTMLEmailChannel, self).__init__(**kw)

    def render(self, row, data, style=''):
        send_params = emailproc.build_multipart_mail(
                       env, ptenv, row, data, self.tempreg)
        return send_params

    def send(self, row, data, style=''):
        #TODO: roll this into parent class - unify params
        # print 'HTMLEMailChan sending to %s %s' % (row, data)
        send_params = self.render(row, data, style)
        self.dest.mpart_send(**send_params)
        return self.dest


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
