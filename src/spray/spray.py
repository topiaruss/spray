import argparse
import atexit
import ConfigParser
import logging
import signal
import subprocess
import sys

LOG = logging.getLogger(__name__)

def get_config(cf):
    cf = open('spray.cfg', 'r')
    config = ConfigParser.RawConfigParser()
    config.readfp(cf)
    return config

class ForgivingFileType(argparse.FileType):
    def __call__(self, string):
        try:
            super(ForgivingFileType,self).__call__(string)
        except IOError as err:
            print err

def get_command_line_args():
    parser = argparse.ArgumentParser(
      description='Spray messaging daemon for Sponsorcraft website')
    parser.add_argument('-c', '--config_file', metavar='file',
      type=ForgivingFileType('r'), default='spray.cfg',
      help='a config file (defaults to spray.cfg)')

    # parser.add_argument('-p', '--port', dest='port',
    #                     help='the port to bind to')
    return parser.parse_args()


def cleanup():
    print "cleanup"

def on_exit(sig, frame):
    print "exit"
    LOG.info("exiting Server on SIGINT")
    exit(1)

def app():
    print "hi"
    #atexit.register(cleanup)

    args = get_command_line_args()
    config = get_config(args.config_file)

    level = eval(config.get('Logging', 'level'))
    format = config.get('Logging', 'format')
    lfile = config.get('Logging', 'filename')
    logging.basicConfig(level=level, format=format, filename=lfile)
    signal.signal(signal.SIGINT, on_exit)

    while 1:
        print 1


