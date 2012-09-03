import os
import ConfigParser


S3CFG_FILE = '.s3cfg'


def get_aws_config():
    "Looks for convenient AWS keys"
    try:
        path = os.path.join(os.path.expanduser('~'), S3CFG_FILE)
        config = ConfigParser.RawConfigParser()
        success = config.read(path)
        if not success:
            print 'Found no %s config file' % path
        acc = config.get('default', 'access_key')
        sec = config.get('default', 'secret_key')
        return (acc, sec)
    except:
        print "You are probably missing a .s3cfg file - Russ can help."
        import sys
        sys.exit(1)
