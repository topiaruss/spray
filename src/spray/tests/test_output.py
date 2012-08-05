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
        assert set(items) == set([('email', 'SimpleTemplateRegistry')])

    def test_add_a_registry(self):
        output.AVAILABLE_TEMPLATE_REGISTRIES = {}
        output.SimpleTemplateRegistry.make_available('email')
        tr_instance = output.AVAILABLE_TEMPLATE_REGISTRIES['email']
        assert tr_instance.__class__.__name__ == "SimpleTemplateRegistry"


class TestChannel(unittest.TestCase):

    destination=output.DESTINATION_REGISTRY['DummyDestination']()

    def test_autoinit_to_email_channel_from_default_templ_reg(self):
        ch = output.Channel(medium='email',
          destination=self.destination)
        assert ch.tempreg == output.AVAILABLE_TEMPLATE_REGISTRIES['email']

    def test_init_to_custom_registry(self):
        reg = output.SimpleTemplateRegistry()
        ch = output.Channel(medium='email',  tempreg=reg,
          destination=self.destination)
        assert ch.tempreg == reg

    def test_select_custom_from_available_registry(self):
        class SubTemplate(output.SimpleTemplateRegistry):
            pass
        SubTemplate.make_available('foo')
        ch = output.Channel(medium='email',  tempreg='foo',
          destination=self.destination)
        assert isinstance(ch.tempreg, SubTemplate)
