from spray import hub
import argparse
import ConfigParser
import logging


class Source(object):
    """Represents ...
    """
    def __init__(self, name, send_queue=None):
        assert type(name) == str
        self.name = name
        our_hub = hub.Hub()
        if send_queue is None:
            # just create a queue named after the source
            self.send_queue = our_hub.get_or_create(name)
        elif isinstance(send_queue, str):
            # user wants us to make a queue with certain name
            self.send_queue = our_hub.get_or_create(send_queue)
        else:
            # use queue we were handed
            self.send_queue = send_queue

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode("utf-8")

    def send(self, event_id, data={}):
        """Sends the event with passed event_id and data to the queue.
        """
        assert type(event_id) == str
        assert type(data) == dict

        self.send_queue.create_and_send(event_id, data)


class ClientApp():

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
        return pp.pars

    def config_logging(self, config):
        level = eval(config.get('Logging', 'level'))
        format = config.get('Logging', 'format')
        lfile = config.get('Logging', 'filename')
        logging.basicConfig(level=level, format=format, filename=lfile)

    def config_app(self, config):
        qq = hub.HUB.get_or_create('test')
        me = Source('me', qq)
        crafter_data = dict(name='Russ Ferriday',
          email='russf@topia.com')
        me.send("system.project.created", crafter_data)

    def __call__(self):
        "simple command line action"

        arg = self.get_command_line_args()
        config = self.get_config(arg.config_file)
        self.config_logging(config)
        self.config_app(config)


def app():
    ClientApp()()
