# emailproc.py - bits and pieces of email processing
import logging
from spray.utils import unescape

LOG = logging.getLogger(__name__)

FROM_ADDRESS = 'info@sponsorcraft.com'
BCC_ADDRESSES = set(['bcc-dump@sponsorcraft.com'])
BCC_ADDRESSES = set([])
ADMIN_ADDRESSES = set('rf@sponsorcraft.com jm@sponsorcraft.com '
  'dk@sponsorcraft.com'.split())


def build_multipart_mail(env, ptenv, row, data, tempreg):
    params = {}

    # get sender from data / row / constant
    params['source'] = data.get('from') or \
                       row.get('from') or FROM_ADDRESS

    toa = set(data.get('to', tuple()))

    # accumulate all the recipient types, if present
    for recipient in row['recipient']:
        recipient = data.get('%s_email_address' % recipient)
        if recipient:
            toa = toa.union([recipient])

    params['to_addresses'] = list(toa)

    # add admins to BCC if 'bcc_admin' is in matrix.recipient
    direct_bcc = data.get('bcc') or BCC_ADDRESSES
    matrix_bcc = 'bcc:admin' in row['recipient'] and ADMIN_ADDRESSES or set([])
    params['bcc_addresses'] = list(direct_bcc.union(matrix_bcc))

    # subject comes from the row, not the data, so we use it two ways
    subject = row['subject_en-gb']
    params['subject'] = subject
    data['subject'] = subject

    rawtext = row['body_en-gb']
    unescaped = unescape.unescape(rawtext)
    lines = unescaped.split('\\n')

    # create the html version
    template = env.from_string('<br/>\n'.join(lines))  # TODO: Cache?
    body = template.render(data)
    data['body'] = body
    style = row.get('body_fmt', '')
    site = data.get('site_name', '')
    params['html_body'] = tempreg.render(data, style, site)

    # text version
    template = ptenv.from_string('\n'.join(lines))  # TODO: Cache?
    body = template.render(data)
    params['text_body'] = body
    params['body'] = None  # MUST FORCE AWS TO DO MULTIPART

    LOG.debug('mpart data %s' % data)
    LOG.debug('mpart params %s' % params)
    return params
