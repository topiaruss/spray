from spray import output
import unittest


class TestAmazonSESDestination(unittest.TestCase):

    def test_instance(self):
        ses = output.AmazonSESDestination()
        ses = ses  # fake-out syntax checker

    def test_send(self):
        ses = output.AmazonSESDestination()
        #these addresses work, since I have enabled them in my AWS SES sandbox
        data = {'from': 'rf@sponsorcraft.com', 'subject': 'some subject',
                    'to': ['russf@topia.com']}
        body = """hi russ,
        nice to see you!"""
        ses.send(body, data)


class TestDefaultDestinationRegistryEntries(unittest.TestCase):

    def test_dummy_destination_entry(self):
        dest = output.DESTINATION_REGISTRY['DummyDestination']
        assert dest

    def test_mock_destination_entry(self):
        dest = output.DESTINATION_REGISTRY['MockSmtpDestination']
        assert dest

    def test_AWS_destination_entry(self):
        dest = output.DESTINATION_REGISTRY['AmazonSESDestination']
        assert dest


class TestTemplateRegistration(unittest.TestCase):

    def test_available_dict_present(self):
        assert hasattr(output, "AVAILABLE_TEMPLATE_REGISTRIES")

    def test_default_template_registries(self):
        items = [(k, v.__class__.__name__) for k, v in\
          output.AVAILABLE_TEMPLATE_REGISTRIES.items()]
        assert set(items) == set([('email', 'TemplateRegistry')])

    def test_add_a_registry(self):
        output.AVAILABLE_TEMPLATE_REGISTRIES = {}
        output.TemplateRegistry.make_available('email')
        tr_instance = output.AVAILABLE_TEMPLATE_REGISTRIES['email']
        assert tr_instance.__class__.__name__ == "TemplateRegistry"


