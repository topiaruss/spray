# emailproc.py - bits and pieces of email processing
import jinja2
import logging
import stoneagehtml

LOG = logging.getLogger(__name__)

FROM_ADDRESS = 'info@sponsorcraft.com'
BCC_ADDRESSES = set(['bcc-dump@sponsorcraft.com'])
ADMIN_ADDRESSES = set('rf@sponsorcraft.com jm@sponsorcraft.com '
  'dk@sponsorcraft.com'.split())


def build_multipart_mail(row, data, tempreg):
    params = {}

    # get sender from data / row / constant
    params['source'] = data.get('from') or \
                       row.get('from') or FROM_ADDRESS

    toa = set(data.get('to'))

    # accumulate all the recip types, if present
    for recip in 'crafter sponsor follower'.split():
        recip = data.get('%s_email_address' % recip)
        if recip:
            toa = toa.union([recip])

    params['to_addresses'] = list(toa)

    # add admins to BCC if 'bcc_admin' is in matrix.recipient
    direct_bcc = data.get('bcc') or BCC_ADDRESSES
    matrix_bcc = 'bcc:admin' in row['recipient'] and ADMIN_ADDRESSES
    params['bcc_addresses'] = list(direct_bcc.union(matrix_bcc))

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
    space_age = tempreg.render(data, style)
    stone_age = stoneagehtml.compactify(space_age)
    params['html_body'] = stone_age

    # text version
    template = jinja2.Template('\n'.join(lines))  # TODO: Cache?
    body = template.render(data)
    params['text_body'] = body
    params['body'] = None  # MUST FORCE AWS TO DO MULTIPART

    LOG.debug('mpart data %s' % data)
    LOG.debug('mpart params %s' % params)
    return params
