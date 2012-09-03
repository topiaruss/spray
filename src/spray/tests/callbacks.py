from spray import client


def crafter_first_name_callback(crafter):
    print 'kilroy'
    return 'crafty'

crafter_first_name_callback.token_id = 'crafter_first_name'


def project_preview_url_callback(project):
    print 'roger'
    return 'sillyproject'

project_preview_url_callback.token_id = 'project_preview_url'

client.register_callback(crafter_first_name_callback)
client.register_callback(project_preview_url_callback)
