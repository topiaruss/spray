from spray import output
import unittest


class TestAmazonSESDestination(unittest.TestCase):

    def test_instance(self):
        ses = output.AmazonSESDestination()
        if ses:  #fakeout syntax checker
            ses = ses

    def test_send(self):
        ses = output.AmazonSESDestination()
        #these addresses work, since I have enabled them in my AWS SES sandbox
        data = {'from': 'rf@sponsorcraft.com', 'subject': 'some subject',
                    'to': ['russf@topia.com']}
        body = """hi russ,
        nice to see you!"""
        ses.send(body, data)
