from spray import action
from spray import matrix
from spray import output
import argparse
import ConfigParser
import logging
import signal

LOG = logging.getLogger(__name__)


class ConfWrap(object):

    def __init__(self, cf):
        self.config = config = ConfigParser.RawConfigParser()
        config.readfp(cf)

    def get(self, section, option):
        try:
            return self.config.get(section, option)
        except ConfigParser.NoOptionError:
            return None

    def items(self, section):
        return self.config.items(section)


def get_config(cf):
    return ConfWrap(cf)


def get_command_line_args():
    pp = argparse.ArgumentParser(
      description='Spray messaging daemon for Sponsorcraft website')
    pp.add_argument('-c', '--config_file', metavar='file',
      type=argparse.FileType('r'), default='sprayd.cfg',
      help='a config file (defaults to sprayd.cfg)')
    return pp.parse_args()


def cleanup():
    print "cleanup"


def on_exit(sig, frame):
    print "exit"
    LOG.info("Exiting Server on SIGINT")
    exit(1)


def config_logging(config):
    level = eval(config.get('Logging', 'level'))
    format = config.get('Logging', 'format')
    lfile = config.get('Logging', 'filename')
    logging.basicConfig(level=level, format=format, filename=lfile)


def config_app(config):

    #get the matrix
    matrix_type = config.get('ActionMatrix', 'type')
    kw = dict(config.items('ActionMatrix')[1:])
    kw.update(dict(credentials=matrix.Credentials()))
    mm = matrix.matrixFactory(matrix_type, kw)
    mm.update()

    def get_override(config, k):
        v = config.get('RecipientOverride', k)
        return v and v.split() or ()

    overrides = dict(
        to_addresses=get_override(config, 'to_addresses'),
        cc_addresses=get_override(config, 'cc_addresses'),
        bcc_addresses=get_override(config, 'bcc_addresses'),
    )

    dest = output.DESTINATION_REGISTRY['AmazonSESDestination'](
      overrides=overrides)

    # this overwrites the default, which is a simple Channel()
    email_channel = output.HTMLEmailChannel(medium='email', destination=dest)
    output.CHAN_REG.register(email_channel)

    #this will start running immediately
    the_processor = action.Processor('testSQS', mm)
    assert the_processor  # trick the syntax checker


def app(testing=False):

    #TODO: improve testing. Currently we only ensure that imports work
    if testing:
        return

    print "starting sprayd"

    arg = get_command_line_args()
    config = get_config(arg.config_file)
    config_logging(config)
    signal.signal(signal.SIGINT, on_exit)

    config_app(config)



