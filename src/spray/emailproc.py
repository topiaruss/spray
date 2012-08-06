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

        import pdb; pdb.set_trace()
        rawtext = row['body_en_uk']
        lines = rawtext.split('\\n')
        brlines = '<br/>\n'.join(lines)
        template = jinja2.Template(brlines)  # TODO: Cache?
        body = template.render(data)
        data['body'] = body

        params['text_body'] = '\n'.join(lines)
        params['body'] = None  # MUST FORCE AWS TO DO MULTPPART
        style = row.get('body_fmt', '')
        params['html_body'] = tempreg.render(data, style)
        LOG.debug('mpart data %s' % data)
        LOG.debug('mpart params %s' % params)
        return params
