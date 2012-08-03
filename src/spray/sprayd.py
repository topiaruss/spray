import argparse
import ConfigParser
import logging
import signal

LOG = logging.getLogger(__name__)


def get_config(cf):
    config = ConfigParser.RawConfigParser()
    config.readfp(cf)
    return config


class ForgivingFileType(argparse.FileType):
    def __call__(self, name):
        try:
            super(ForgivingFileType, self).__call__(name)
        except IOError as err:
            print err
            raise err


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
    LOG.info("exiting Server on SIGINT")
    exit(1)


def app():
    print "hi"
    #atexit.register(cleanup)

    arg = get_command_line_args()
    config = get_config(arg.config_file)

    level = eval(config.get('Logging', 'level'))
    format = config.get('Logging', 'format')
    lfile = config.get('Logging', 'filename')
    logging.basicConfig(level=level, format=format, filename=lfile)
    signal.signal(signal.SIGINT, on_exit)

    


