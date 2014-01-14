try:
    from django.conf import settings as djsettings
    assert djsettings  # bypass the syntax checker
except:
    djsettings = {}

DEFAULT_SETTINGS = dict()

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(djsettings, 'SPRAY_SETTINGS', {}))

globals().update(USER_SETTINGS)
