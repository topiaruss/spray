# emailproc.py - bits and pieces of email processing
import jinja2

TEMP_FROM_ADDRESS = 'rf@sponsorcraft.com'
TEMP_BCC_ADDRESS = 'asdf'

def build_multipart_mail(row, data, tempreg):
        params = {}

        #TODO - get sender from row (update spreadsheet)
        params['source'] = row.get('from', None) or TEMP_FROM_ADDRESS
        params['to_addresses'] = data['recipients']
        #params['bcc_addresses'] = TEMP_BCC_ADDRESS
        params['subject'] = row['subject_en_uk']

        # render the plaintext part, and store in the data
        #   for use by the html render stage
        template = jinja2.Template(row['body_en_uk'])  # TODO: Cache?
        body = template.render(data)
        data['body'] = body
        params['text_body'] = body
        params['body'] = None
        style = row.get('body_fmt', '')
        params['html_body'] = tempreg.render(data, style)
        return params
