# -*- coding: utf-8 -*-

from spray import emailproc
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

    def _build_dummy_mpart_send_data(self):
        row, data = {}, {}
        row['from'] = 'rf@sponsorcraft.com'
        row['subject_en_uk'] = 'søme silly sübject'
        row['body_en_uk'] = 'Hello {{ first_name }} !'
        row['recipient'] = 'crafter,bcc:admin'
        data['first_name'] = 'Russ'
        data['to'] = ('russf@topia.com',)
        return row, data

    def test_mpart_send(self):
        ses = output.AmazonSESDestination()
        tr = output.SimpleTemplateRegistry()
        tr.register('', "<head></head><body>{{ body }}</body>")
        row, data = self._build_dummy_mpart_send_data()
        mpart_params = emailproc.build_multipart_mail(row, data, tr)
        ses.mpart_send(**mpart_params)


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


class TestFSBasedTemplateReg(unittest.TestCase):

    def test_instantiation_without_params(self):
        self.assertRaises(KeyError, output.FSBasedTemplateRegistry)

    def test_instantiation_with_default_dir(self):
        tt = output.FSBasedTemplateRegistry(templates_dir='./templates/email')
        tt = tt  # defeat editor checking

    def test_lookup_default_template(self):
        tt = output.FSBasedTemplateRegistry(templates_dir='./templates/email')
        default = tt.lookup('')
        from jinja2 import Template
        assert isinstance(default, Template)


class TestChannel(unittest.TestCase):

    destination = output.DESTINATION_REGISTRY['DummyDestination']()

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


class TestJinjaUrlFilter(unittest.TestCase):

    def setUp(self):
        from jinja2 import Environment
        from spray import templating
        self.env = env = Environment()
        env.filters['urlformat'] = templating.urlformat

    def test_bare_url_filter(self):
        test_bareurl = self.env.from_string("blah {{ u1|urlformat }} de blah")
        result = test_bareurl.render(u1='https://sc.com')
        expect = u'blah <a href="https://sc.com">https://sc.com</a> de blah'
        assert result == expect

    def test_url_with_text_filter(self):
        test_bareurl = self.env.from_string(
          "blah {{ u1|urlformat('click') }} de blah")
        result = test_bareurl.render(u1='https://sc.com')
        expect = u'blah <a href="https://sc.com">click</a> de blah'
        assert result == expect


class TestJinjaButtonFilter(unittest.TestCase):

    def setUp(self):
        from jinja2 import Environment
        from spray import templating
        self.env = env = Environment()
        env.filters['buttonformat'] = templating.buttonformat

    def test_bare_url_filter(self):
        test_bareurl = self.env.from_string("{{ u1|buttonformat }}")
        result = test_bareurl.render(u1='https://sc.com')
        assert 'sc.com' in result

    def test_url_with_text_filter(self):
        test_url = self.env.from_string(
          """{{ u1|buttonformat(fcolour=fcolour,
            bcolour=bcolour, text=text, font=font) }}""")
        kw = dict(u1='https://sc.com',
          bcolour='BCOL', fcolour='FCOL', text='TXT', font='FFONT')
        result = test_url.render(**kw)
        for v in kw.values():
            assert v in result
