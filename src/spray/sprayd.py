from spray import action
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
    LOG.info("Exiting Server on SIGINT")
    exit(1)


def config_logging(config):
    level = eval(config.get('Logging', 'level'))
    format = config.get('Logging', 'format')
    lfile = config.get('Logging', 'filename')
    logging.basicConfig(level=level, format=format, filename=lfile)


def config_app(config):
    #import pdb; pdb.set_trace()

    #get the matrix
    matrix_type = config.get('ActionMatrix', 'type')
    kwargs = dict(config.items('ActionMatrix')[1:])
    matrix = action.matrixFactory(matrix_type, kwargs)

    #the_processor = action.Processor('send', matrix, running=False)
    #this will start running immediately
    the_processor = action.Processor('send', matrix)



def app():
    print "hi"
    #atexit.register(cleanup)

    arg = get_command_line_args()
    config = get_config(arg.config_file)
    config_logging(config)
    signal.signal(signal.SIGINT, on_exit)

    config_app(config)



