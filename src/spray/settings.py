try:
    from django.conf import djsettings
    assert djsettings  # bypass the syntax checker
except:
    djsettings = {}

DEFAULT_SETTINGS = dict(

    #  For our tests, we assume that a single client is able to
    #  access both ends of the message queue and the email service
    CREDENTIALS_FILENAME='spray.client',

)

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(djsettings, 'SPRAY_SETTINGS', {}))

globals().update(USER_SETTINGS)
