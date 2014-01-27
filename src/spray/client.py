from spray import hub
from spray import matrix
from spray import sprayd
from spray.utils import unescape
from StringIO import StringIO
import argparse
import ConfigParser
import inspect
import logging
import time

from django.conf import settings
SITE_ID = settings.SITE_ID


# Note: some imports are deferred for conditional loading

LOG = logging.getLogger(__name__)

CALLBACKS = {}


def register_callback(func):
    token_id = func.token_id
    CALLBACKS[token_id] = func


class Assembler(object):

    def __init__(self, mm, event_id, context):
        self.matrix = mm
        self.event_id = event_id
        self.context = context
        self.results = None
        self.syntax_error = self.broken_template = None

    def assemble(self):
        self._do_callbacks(self.event_id, self.context)

    def get_undef_body_fields(self, template):
        "returns the tokens from a jinja template"
        from jinja2 import meta, TemplateSyntaxError
        from spray import jinjaenv
        env = jinjaenv.env
        try:
            if template is None:
                template = ''
            unescaped = unescape.unescape(template)
            ast = env.parse(unescaped)
            return tuple(meta.find_undeclared_variables(ast))
        except TemplateSyntaxError as e:
            self.syntax_error = (e.message, 'line: %s' % e.lineno)
            self.broken_template = template
            LOG.exception("Broken token - possibly a space in {{}}. %s. Template: %s" %
              (self.syntax_error, template))
            raise

    def get_undef_addr_fields(self, event_id, act_type, recipient_cell):
        "parse the recipient cell from the spreadsheet, ret a list of addrs or ()"
        try:
            # this is to fix django recip cells, which are lists.
            if type(recipient_cell) in [str, unicode]:
                recipient_cell = recipient_cell.split(',')
            assert type(recipient_cell == list)
            recipients = [r.strip() for r in recipient_cell]
            ignores = ('bcc:admins',)
            pat = '%s_%s_address'
            ret = [(pat % (r, act_type)) for r in recipients if r not in ignores]
            return [str(r) for r in ret]
        except Exception as e:
            print e
            LOG.exception("Prob in recip field: eid: %s, actn: %s, recpcell: %s" %
            (event_id, act_type, recipient_cell))
            return ()

    def get_required_args(self, func):
        "return a list of the arg names required http://bit.ly/TgqZQX"
        args, varargs, varkw, defaults = inspect.getargspec(func)
        if defaults:
            args = args[:-len(defaults)]
        return args

    def get_event_field_tokens(self, event_id=None, site_id=None):
        "returns the tokens for ALL rows under an event"
        rows = self.matrix.get_rows_for_event(event_id, site_id)
        events = {}
        for r in rows:
            eid = r['event_id']
            # get the tokens needed for the body fields
            bfields = [v for k, v in r.items() if k.startswith('body')\
                       or k.startswith('subject')]
            for f in bfields:
                events.setdefault(eid, []).extend(
                  self.get_undef_body_fields(f))
            # get the tokens needed for the recipient field
            events.setdefault(eid, []).extend(self.get_undef_addr_fields(
              eid, r['action_type'], r['recipient']))
        # uniquify
        fevents = {}
        for k, v in events.items():
            fevents[k] = sorted(list(set(v)))
        events = fevents
        if len(events) == 1:
            return events.values()[0]
        return events

    def _do_callbacks(self, event_id, context):
        if not context.has_key('site_id'):
            context['site_id'] = SITE_ID

        # the tokens we need for this event
        tokens = self.get_event_field_tokens(event_id, site_id=context['site_id'])

        fields_to_expand = {'follower_first_name': 'project__followers_first_name',}
        for singular_token, plural_token in fields_to_expand.items():
            if singular_token in tokens:
                tokens = [token for token in tokens if token != singular_token]  # Remove singular token
                tokens.append(plural_token)

        # tokens we know we can't do -- no callbacks for them
        unfilled = set(tokens).difference(set(CALLBACKS.keys()))

        # the callbacks we want to try
        cbs = set(tokens).intersection(set(CALLBACKS.keys()))

        # list of required source objects not found in the context
        no_source = set()
        #results = context.copy()  #  < -- was !
        results = {}
        for k in cbs:
            c = CALLBACKS[k]
            reqargs = set(self.get_required_args(c))
            available = set(context.keys())
            if available.issuperset(reqargs):
                try:
                    reqargs = sorted(list(reqargs))
                    # MUST sort all callback params
                    results[k] = c(*[context[v] for v in reqargs])
                except Exception as e:
                    LOG.exception('failure %s in callback %s for %s with %s' % (e, c, k, context))
                    results[k] = '...'  # This will flag an exception in msg
            else:
                no_source = no_source.union(reqargs - available)

        results['site_id'] = context['site_id']  # Make sure we always have a site_id for the backend, regardless of callbacks params
        self.results = dict(no_source=no_source, unfilled=unfilled, results=results)
        return self.results


class Source(object):
    """Represents the client side of an interaction.
       Currently only worries about sending.
    """
    def __init__(self, name, send_queue=None, matrix=None):
        assert type(name) == str
        self.name = name
        self.matrix = matrix
        if send_queue is None:
            # just create a queue named after the source
            our_hub = hub.HUB
            self.send_queue = our_hub.get_or_create(name)
        elif isinstance(send_queue, str):
            # user wants us to make a queue with certain name
            # that's different from our source name
            our_hub = hub.HUB
            self.send_queue = our_hub.get_or_create(send_queue)
        else:
            # use queue we were handed
            self.send_queue = send_queue

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode("utf-8")

    def _send(self, event_id, data={}):
        """Sends the event with passed event_id and data to the queue."""
        assert type(event_id) in (str, unicode)
        assert type(data) == dict

        self.send_queue.create_and_send(event_id, data)

    def send(self, event_id, context={}):
        if 'site_id' not in context:
            context['site_id'] = SITE_ID

        ret = dict(unfilled=[], no_source=[], results={})
        if self.matrix is not None:
            assembler = Assembler(self.matrix, event_id, context)
            assembler.assemble()
            context = assembler.results['results']
            ret = assembler.results

        self._send(event_id, context)
        return ret

#
# class ClientApp(object):
#     """ Simple app to send a message to a queue.
#         config.app provides a usage example
#     """
#
#     def get_config(self, cf):
#         config = ConfigParser.RawConfigParser()
#         config.readfp(cf)
#         return config
#
#     def get_command_line_args(self):
#         pp = argparse.ArgumentParser(
#           description='Spray messaging daemon for Sponsorcraft website')
#         pp.add_argument('-c', '--config_file', metavar='file',
#           type=argparse.FileType('r'), default='sprayd.cfg',
#           help='a config file (defaults to sprayd.cfg)')
#         return pp.parse_args()
#
#     def config_logging(self, config):
#         level = eval(config.get('Logging', 'level'))
#         format = config.get('Logging', 'format')
#         lfile = config.get('Logging', 'filename')
#         logging.basicConfig(level=level, format=format, filename=lfile)
#
#     def config_app(self, config):
#         me = Source('me', 'testSQS')
#         event_id = "sponsor.project.fundingtarget"
#         project_data = dict(user_first_name='Test User', name="Testing", to=('pf@sponsorcraft.com',))
#         me.send(event_id, project_data)
#         print "sent %s" % event_id
#
#     def __call__(self):
#         "simple command line action"
#
#         arg = self.get_command_line_args()
#         config = self.get_config(arg.config_file)
#         self.config_logging(config)
#         self.config_app(config)


#This is used by setup.py and buildout.cfg to generate an app in bin/
# def app():
#     ClientApp()()

CALLBACK_HEADER = """# When implementing a callback, refine the context
# name, from the bulky template, then access the data from that
# callback. The existence of the  appropriate structure will be checked
# during the call, and the client notified of any shortages.

from spray import client

"""

import string
template = string.Template("""
# Used for...
# $used
def ${cb}_callback(crafter_user_project_system):
    return '[${cb}]'

${cb}_callback.token_id = '${cb}'
client.register_callback(${cb}_callback)

""")

#
# class DryRun(object):
#     """ Simple app to create a sample email to all event_id
#     """
#
#     def get_config(self, cf):
#         config = ConfigParser.RawConfigParser()
#         config.readfp(cf)
#         return config
#
#     def config_logging(self, config):
#         level = eval(config.get('Logging', 'level'))
#         format = config.get('Logging', 'format')
#         lfile = config.get('Logging', 'filename')
#         logging.basicConfig(level=level, format=format, filename=lfile)
#
#     def get_command_line_args(self):
#         pp = argparse.ArgumentParser(
#           description='Send all the messages on the config page')
#
#         pp.add_argument('-c', '--config_file', metavar='file',
#           type=argparse.FileType('r'), default='dryrun.cfg',
#           help='a config file (defaults to sprayd.cfg)')
#
#         pp.add_argument('-q', '--queue', default='',
#           help='the queue you want to send to (defaults to sprayd.cfg)')
#
#         pp.add_argument('-m', '--matrix', default='',
#           help='the matrix to test (defaults to our main matrix)')
#
#         pp.add_argument('-t', '--to', default='',
#           help='the delivery email address(es) (defaults to russf@topia.com)')
#
#         # pp.add_argument('-s', '--stuffing', default='',
#         #   help='the matrix to stuff from (defaults to our main matrix)')
#
#         return pp.parse_args()
#
#     def config_app(self, config, arg):
#         self.recip = arg.to.split() or config.get('Email', 'recip').split()
#         self.sender = config.get('Email', 'from')
#         self.bcc = config.get('Email', 'bcc').split()
#
#         # setup a matrix
#         url = arg.matrix or config.get('ActionMatrix', 'url')
#         if url.startswith('http'):
#             creds = matrix.Credentials()
#             self.mm = matrix.GoogleActionMatrix(creds, url)
#         else:
#             self.mm = matrix.CSVActionMatrix(url)
#         self.mm.update()
#
#         #now setup a queue, but with a custom matrix
#         queue = arg.queue or config.get('Queue', 'queue') or 'testSQS'
#         self.me = Source('me', queue, self.mm)
#
#     #TODO setup stuffing
#     # surl = arg.stuffing or config.get('Stuffing', url)
#     # surl = surl
#     def build_stuffing(self):
#         self.context = dict(project=dict(),
#                             user=dict(),
#                             system=dict())
#
#     def explore_events(self):
#         "summarizes the callbacks needed and for which events"
#         events = self.mm.data.keys()
#         needs = {}
#         for e in events:
#             tokens = self.me.get_event_field_tokens(e)
#             needs[e] = tokens
#         depends = {}
#         for k, v in needs.items():
#             for token in v:
#                 depends.setdefault(token, set()).add(k)
#         return depends
#
#     def put_callbacks(self, depends):
#         """Generates a file with all the callback stubs we know about.
#         This will be in the execution directory. It may be necessary to
#         move it to the tests directory where we keep a fresh copy.
#         """
#         keys = sorted(depends.keys())
#         with open('fullcallbacks.py', 'w') as ff:
#             ff.write(CALLBACK_HEADER)
#             for k in keys:
#                 used = sorted(depends[k])
#                 used = '\n# '.join(used)
#                 ff.write(template.substitute({'cb': k, 'used': used}))
#
#     def blast_events(self):
#         "blast one message for each event_id"
#
#         # retain next line for registry side-effects of import
#         from spray.tests import fullcallbacks
#         if fullcallbacks:
#             pass  # defeat PEP8 checker
#
#         events = sorted(self.mm.data.keys())
#         for e in events:  # [:5]:
#             # print '5 only'
#             # crafter_user_project_system is a dummy context that
#             # satisfies all stubs. It should be dropped as soon as all stubs
#             # are filled.
#             self.me.send(e, {'to': self.recip,
#                              'bcc': self.bcc,
#                              'sender': self.sender,
#                              'crafter_user_project_system': {}})
#
#     def __call__(self):
#         "heed the call!"
#
#         arg = self.get_command_line_args()
#         config = self.get_config(arg.config_file)
#         self.config_logging(config)
#         self.config_app(config, arg)
#         self.build_stuffing()
#         #  messy, but we enable these two lines to generate a fresh callback
#         #    from the current data.
#         #  depends = self.explore_events()
#         #  self.put_callbacks(depends)
#         self.blast_events()
#
#
# #This is used by setup.py and buildout.cfg to generate an app in bin/
# def dryrun():
#     DryRun()()


SPRAYUI_CONFIG = """
[Logging]
level = logging.DEBUG
format = %(asctime)s-%(levelname)s-%(module)s-%(message)s
filename = sprayui.log

# split with spaces - no commas
[RecipientOverride]
to_addresses = test-override@sponsorcraft.com

[ActionMatrix]
# this is the matrix that will be used for the processor
type = DjangoActionMatrix

#bit of a misnomer - any queue type, predefined.
[SQSQueue]
name = sprayui

[EmailDestination]
name = DummyAmazonSESDestination
"""


class ProcessBox(object):

    def __init__(self, config=None, matrix=None, *args, **kwargs):
        if config is None:
            sio = StringIO(SPRAYUI_CONFIG)
            config = sprayd.ConfWrap(sio)
        self.config = config
        self.tracing = kwargs.get('tracing')
        self.proc = sprayd.processor_factory(config, matrix)

    def grind(self):
        # this is a kludge while we hope that processing continues
        while len(self.proc.queue.queue):
            time.sleep(0.1)
        time.sleep(0.2)

    def stop(self):
        self.proc.stop()

    def get_evidence(self):
        "returns [step][action][replica]{row:row, traffic:traffic}"
        entrails = []
        # Break gracefully if no actions have been run
        try:
            entrails = self.proc.entrails
        except AttributeError:
            pass
        return entrails
