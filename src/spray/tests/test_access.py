from boto import connect_ses
from boto import ses
from boto.sqs import regions
from boto.sqs.connection import SQSConnection
from spray.utils import aws_credentials
import unittest
from . import TEST_CREDENTIALS_FILENAME

class TestCredentials(unittest.TestCase):

    def test_credentials_decode(self):
        "if this fails, you need to put a credentials file in prj/etc/"
        creds = aws_credentials.get_credentials(TEST_CREDENTIALS_FILENAME)
        assert len(creds) == 2

    def test_credentialled_SQS_access(self):
        "check that the credentials can access the SQS service"
        creds = aws_credentials.get_credentials(TEST_CREDENTIALS_FILENAME)
        region_name = 'eu-west-1'
        region = [r for r in regions() if r.name == region_name][0]
        conn = SQSConnection(aws_access_key_id=creds[0],
          aws_secret_access_key=creds[1],
          region=region)
        q = conn.create_queue("PLEASE_KEEP_FOR_TESTING", 30)
        assert q

    def test_credentialled_SES_access(self):
        "check that the credentials can access the SES service"
        creds = aws_credentials.get_credentials(TEST_CREDENTIALS_FILENAME)
        region_name = 'eu-west-1'
        region = ses.get_region(region_name)
        conn = connect_ses(aws_access_key_id=creds[0],
          aws_secret_access_key=creds[1],
          region=region)
        verified = conn.list_verified_email_addresses()
        assert len(verified) > 0
