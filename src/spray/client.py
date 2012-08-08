from spray import hub
from spray import matrix
import argparse
import ConfigParser
import logging

LOG = logging.getLogger(__name__)


def get_undef(template):
    from jinja2 import Environment, meta, TemplateSyntaxError
    env = Environment()
    try:
        ast = env.parse(template)
        return tuple(meta.find_undeclared_variables(ast))
    except TemplateSyntaxError as e:
        print e
        print template
        LOG.exception("Broken token - possibly a space in {{}}")
        return ()


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
        """Sends the event with passed event_id and data to the queue.
        """
        assert type(event_id) == str
        assert type(data) == dict

        self.send_queue.create_and_send(event_id, data)

    def send(self, event_id, context={}):
        self._send(event_id, context)
        return dict(unfilled=[], no_source=[])

    def get_event_field_tokens(self, event_id=None):
        rows = self.matrix.get_rows_for_event(event_id)
        events = {}
        for r in rows:
            bfields = [v for k, v in r.items() if k.startswith('body')]
            for f in bfields:
                events.setdefault(r['event id'], []).extend(get_undef(f))
        # uniquify
        fevents = {}
        for k, v in events.items():
            fevents[k] = sorted(list(set(v)))
        events = fevents
        if len(events) == 1:
            return events.values()[0]
        return events


class ClientApp():
    """ Simple app to send a message to a queue.
        config.app provides a usage example
    """

    def get_config(self, cf):
        config = ConfigParser.RawConfigParser()
        config.readfp(cf)
        return config

    def get_command_line_args(self):
        pp = argparse.ArgumentParser(
          description='Spray messaging daemon for Sponsorcraft website')
        pp.add_argument('-c', '--config_file', metavar='file',
          type=argparse.FileType('r'), default='sprayd.cfg',
          help='a config file (defaults to sprayd.cfg)')
        return pp.parse_args()

    def config_logging(self, config):
        level = eval(config.get('Logging', 'level'))
        format = config.get('Logging', 'format')
        lfile = config.get('Logging', 'filename')
        logging.basicConfig(level=level, format=format, filename=lfile)

    def config_app(self, config):
        me = Source('me', 'testSQS')
        crafter_data = dict(crafter_first_name='Russ', name="Russ Ferriday",
          to=('russf@topia.com',))
        me.send("system.project.created", crafter_data)
        print "sent"

    def __call__(self):
        "simple command line action"

        arg = self.get_command_line_args()
        config = self.get_config(arg.config_file)
        self.config_logging(config)
        self.config_app(config)

#This is used by setup.py and buildout.cfg to generate an app in bin/
def app():
    ClientApp()()
