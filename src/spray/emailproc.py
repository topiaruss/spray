# emailproc.py - bits and pieces of email processing
import jinja2
import logging

LOG = logging.getLogger(__name__)

TEMP_FROM_ADDRESS = 'rf@sponsorcraft.com'
TEMP_BCC_ADDRESS = 'asdf'


def build_multipart_mail(row, data, tempreg):
        params = {}

        # get sender from data / row / constant
        params['source'] = data.get('from') or \
                           row.get('from') or TEMP_FROM_ADDRESS
        params['to_addresses'] = data.get('to')
        # params['bcc_addresses'] =

        # subject comes from the row, not the data, so we use it two ways
        subject = row['subject_en_uk']
        params['subject'] = subject
        data['subject'] = subject

        rawtext = row['body_en_uk']
        lines = rawtext.split('\\n')

        # create the html version
        template = jinja2.Template('<br/>\n'.join(lines))  # TODO: Cache?
        body = template.render(data)
        data['body'] = body
        style = row.get('body_fmt', '')
        params['html_body'] = tempreg.render(data, style)

        # text version
        template = jinja2.Template('\n'.join(lines))  # TODO: Cache?
        body = template.render(data)
        params['text_body'] = body
        params['body'] = None  # MUST FORCE AWS TO DO MULTIPART

        LOG.debug('mpart data %s' % data)
        LOG.debug('mpart params %s' % params)
        return params
