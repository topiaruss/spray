# -*- coding: utf-8 -*-

from spray import emailproc
from spray import output
from spray import SPRAY_ROOT
import unittest
import os


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
        row['subject_en-gb'] = 'søme silly sübject'
        row['body_en-gb'] = 'Hello {{ first_name }}! <br/> '\
          'How is <a href="https://sponsorcraft.com">this link</a>?'
        #row['recipient'] = 'crafter,bcc:admin'
        row['recipient'] = 'crafter'
        data['first_name'] = 'Russ'
        data['to'] = ('russf@topia.com',)
        return row, data

    def test_mpart_send(self):
        ses = output.AmazonSESDestination()
        tr = output.SimpleTemplateRegistry()
        tr.register('', "<head></head><body>{{ body }}</body>")
        row, data = self._build_dummy_mpart_send_data()
        from spray import jinjaenv
        env, ptenv = jinjaenv.env, jinjaenv.ptenv
        mpart_params = emailproc.build_multipart_mail(
          env, ptenv, row, data, tr)
        ses.mpart_send(**mpart_params)

    def test_mpart_send_safe(self):
        ses = output.AmazonSESDestination()
        tr = output.SimpleTemplateRegistry()
        tr.register('', "<head></head><body>{{ body|safe }}</body>")
        row, data = self._build_dummy_mpart_send_data()
        row['subject_en-gb'] = 'søme silly sübject with safe body'
        from spray import jinjaenv
        env, ptenv = jinjaenv.env, jinjaenv.ptenv
        mpart_params = emailproc.build_multipart_mail(
          env, ptenv, row, data, tr)
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

TEMPL_DIR = os.path.join(SPRAY_ROOT, 'templates')

class TestFSBasedTemplateReg(unittest.TestCase):

    def test_instantiation_without_params(self):
        self.assertRaises(KeyError, output.FSBasedTemplateRegistry)

    def test_instantiation_with_default_dir(self):
        tt = output.FSBasedTemplateRegistry(templates_dir=TEMPL_DIR)
        tt = tt  # defeat editor checking

    def test_lookup_default_template(self):
        tt = output.FSBasedTemplateRegistry(templates_dir=TEMPL_DIR)
        default = tt.lookup('')
        from jinja2 import Template
        assert isinstance(default, Template)

    def test_lookup_explicit_sc_template(self):
        tt = output.FSBasedTemplateRegistry(templates_dir=TEMPL_DIR)
        default = tt.lookup('', site='sponsorcraft_com')
        from jinja2 import Template
        assert isinstance(default, Template)
        self.assertIn('<meta site-name="sponsorcraft_com">', default.render())

    def test_lookup_explicit_sc_internal_template(self):
        tt = output.FSBasedTemplateRegistry(templates_dir=TEMPL_DIR)
        default = tt.lookup('internal', site='sponsorcraft_com')
        from jinja2 import Template
        assert isinstance(default, Template)
        self.assertIn('<meta site-name="sponsorcraft_com">', default.render())

    def test_lookup_explicit_soton_template(self):
        tt = output.FSBasedTemplateRegistry(templates_dir=TEMPL_DIR)
        default = tt.lookup('', site='soton_ac_uk')
        from jinja2 import Template
        assert isinstance(default, Template)
        self.assertIn('<meta site-name="soton_ac_uk">', default.render())


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
        self.ptenv = ptenv = Environment()
        env.filters['urlformat'] = templating.urlformat
        ptenv.filters['urlformat'] = templating.urlformat_to_plain

# --

    def test_bare_url_filter(self):
        test_bareurl = self.env.from_string("Hi {{ u1|urlformat }} Bye")
        result = test_bareurl.render(u1='https://sc.com')
        expect = u'Hi <a class="matrix-anchor" style="color: #29ABE2"'\
          ' href="https://sc.com">https://sc.com</a> Bye'
        assert result == expect

    def test_bare_url_filter_plaintext(self):
        test_bareurl = self.ptenv.from_string("Hi {{ u1|urlformat }} Bye")
        result = test_bareurl.render(u1='https://sc.com')
        expect = u'Hi https://sc.com Bye'
        assert result == expect

# --

    def test_bare_url_filter_literal(self):
        test_bareurl = self.env.from_string(
            "Hi {{ 'https://sc.com'|urlformat }} Bye")
        result = test_bareurl.render()
        expect = u'Hi <a class="matrix-anchor" style="color: #29ABE2"'\
          ' href="https://sc.com">https://sc.com</a> Bye'
        assert result == expect

    def test_bare_url_filter_literal_plaintext(self):
        test_bareurl = self.ptenv.from_string(
            "Hi {{ 'https://sc.com'|urlformat }} Bye")
        result = test_bareurl.render()
        expect = u'Hi https://sc.com Bye'
        assert result == expect

# --

    def test_url_with_text_filter(self):
        test_bareurl = self.env.from_string(
          "Hi {{ u1|urlformat('click') }} Bye")
        result = test_bareurl.render(u1='https://sc.com')
        expect = u'Hi <a class="matrix-anchor" style="color: #29ABE2"'\
          ' href="https://sc.com">click</a> Bye'
        assert result == expect

    def test_url_with_text_filter_plaintext(self):
        test_bareurl = self.ptenv.from_string(
          "Hi {{ u1|urlformat('click here') }} Bye")
        result = test_bareurl.render(u1='https://sc.com')
        expect = u'Hi click here https://sc.com Bye'
        assert result == expect


class TestJinjaButtonFilter(unittest.TestCase):

    def setUp(self):
        from jinja2 import Environment
        from spray import templating
        self.env = env = Environment()
        self.ptenv = ptenv = Environment()
        env.filters['buttonformat'] = templating.buttonformat
        ptenv.filters['buttonformat'] = templating.buttonformat_to_plain

    def test_bare_url_filter(self):
        test_bareurl = self.env.from_string("{{ u1|buttonformat }}")
        result = test_bareurl.render(u1='https://sc.com')
        assert 'sc.com' in result

    def test_bare_url_filter_plaintext(self):
        test_bareurl = self.ptenv.from_string("{{ u1|buttonformat }}")
        result = test_bareurl.render(u1='https://sc.com')
        assert result == 'https://sc.com'

    def test_url_with_text_filter(self):
        test_url = self.env.from_string(
          """{{ u1|buttonformat(fcolour=fcolour,
            bcolour=bcolour, text=text, font=font) }}""")
        kw = dict(u1='https://sc.com',
          bcolour='BCOL', fcolour='FCOL', text='TXT', font='FFONT')
        result = test_url.render(**kw)
        for v in kw.values():
            assert v in result

    def test_url_with_text_filter_plaintext(self):
        test_url = self.ptenv.from_string(
          """{{ u1|buttonformat(fcolour=fcolour,
            bcolour=bcolour, text=text, font=font) }}""")
        kw = dict(u1='https://sc.com',
          bcolour='BCOL', fcolour='FCOL', text='TXT', font='FFONT')
        result = test_url.render(**kw)
        assert result == 'TXT : https://sc.com'


class TestJinjaFeaturetextFilter(unittest.TestCase):

    def setUp(self):
        from jinja2 import Environment
        from spray import templating
        self.env = env = Environment()
        self.ptenv = ptenv = Environment()
        env.filters['featuretext'] = templating.featuretext
        ptenv.filters['featuretext'] = templating.featuretext_to_plain

    def test_bare_filter(self):
        html = self.env.from_string("{{ 'some text'|featuretext }}")
        result = html.render()
        expect = u'<span style="color: #29abe2; '\
          'font-family: arial, sans-serif; font-size:24px">'\
          '<strong>some text</strong></span>'
        assert expect == result

    def test_text_param_filter(self):
        html = self.env.from_string("{{ tt|featuretext }}")
        result = html.render(tt='some text')
        expect = u'<span style="color: #29abe2; '\
          'font-family: arial, sans-serif; font-size:24px">'\
          '<strong>some text</strong></span>'
        assert expect == result

    def test_several_param_filter(self):
        html = self.env.from_string("{{ tt|featuretext(colour='red',"\
          "font='elfvetica',fontsize='2px',formatting='em') }}")
        result = html.render(tt='some text')
        expect = u'<span style="color: red; '\
          'font-family: elfvetica; font-size:2px">'\
          '<em>some text</em></span>'
        assert expect == result

    def test_promotion_of_template_avoids_unicode_error(self):
        # the str is promoted to unicode by jinja...
        html = self.env.from_string(str("a fiver is {{ amount }}"))
        # No render error
        result = html.render(amount=u'\u00A3 5.00')
        expect = u'a fiver is \u00A3 5.00'
        self.assertEqual(expect, result)

class TwilioSmsDestinationTest(unittest.TestCase):
    '''
        IMPORTANT: for this test to work, you
        MUST set up the tokens in the python os.environ.
        To do this: open bin/activate and add the following to the end:

        export TWILIO_SID=XXXXXXXXXXXXXXXXXXXXXXXXXX
        export TWILIO_TOKEN=YYYYYYYYYYYYYYYYY
        export TWILIO_DEFAULT_NUMBER=+44123456789

        and save the file. This will add these values into your environment.
        Make sure to replace the values with your own

    '''

    def setUp(self):
        SID = os.environ['TWILIO_SID']
        CLI = os.environ['TWILIO_TOKEN']
        self.client = output.TwilioSmsDestination(SID,CLI)

    def test_basic_message(self):
        ' This will send an sms to th'
        default_from = os.environ['TWILIO_DEFAULT_NUMBER']
        # This number *will* receive a text message, be warned
        to ='+447943511601'
        self.client.send(to, default_from, 'test_basic_message')

