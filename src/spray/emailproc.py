# emailproc.py - bits and pieces of email processing
import logging
import re
from spray.utils import unescape
from django.conf import settings
from django.contrib.sites.models import Site
LOG = logging.getLogger(__name__)

# TODO: refactor to settings
BCC_ADDRESSES = set(['bcc-dump@sponsorcraft.com'])
ADMIN_ADDRESSES = set('rf@sponsorcraft.com jm@sponsorcraft.com dk@sponsorcraft.com'.split())


def get_from_address(data):
    from_address_map = settings.SPRAY_SETTINGS['FROM_ADDRESSES']
    try:
        return from_address_map[data['site_name']]
    except (KeyError, Exception) as e:
        # log.error('Spray FROM_ADDRESS lookup failed: %s' % e)
        return from_address_map[data['default']]


def build_multipart_mail(env, ptenv, row, data, tempreg):
    params = {}

    # Lookup sender from our static settings map
    params['source'] = get_from_address(data)

    toa = set(data.get('to', tuple()))

    # accumulate all the recipient types, if present
    for recipient in row['recipient']:
        if recipient == 'bcc:admins':
            continue
        is_plural = re.search("^[a-z]+__(?P<singular>[a-z_]+)s$", recipient)
        if is_plural:
            recipient = is_plural.group('singular')
        recipient = data.get('%s_email_address' % recipient)
        if recipient:
            if isinstance(recipient, (str, unicode)):
                recipient = [recipient]
            toa = toa.union(recipient)

    params['to_addresses'] = list(toa)

    # add admins to BCC if 'bcc_admin' is in matrix.recipient
    direct_bcc = data.get('bcc') or BCC_ADDRESSES
    matrix_bcc = 'bcc:admin' in row['recipient'] and ADMIN_ADDRESSES or set([])
    params['bcc_addresses'] = list(direct_bcc.union(matrix_bcc))

    # If we only have BCC and no to address, promote bcc to
    # params['to_addresses'] = params['bcc_addresses']

    # subject comes from the row, not the data, so we use it two ways
    subject = row['subject_en-gb']
    params['subject'] = subject
    data['subject'] = subject

    rawtext = row['body_en-gb']
    unescaped = unescape.unescape(rawtext)
    lines = unescaped.split('\\n')

    # Ensure our strings don't contain unicode (e.g. pledge_amount, message body)
    for k,v in data.items():
        if isinstance(v, str):
            data[k] = v.decode('utf-8')

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
