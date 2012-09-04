"Various test fixures for doctests, etc."
from zope.testing import renormalizing
import doctest
import re

checker = renormalizing.RENormalizing([
    (re.compile(r'<Event [0-9a-f]*::'),
     '<Event 12341234::'),
    (re.compile(r'<SQSEvent [0-9a-f]*::'),
     '<SQSEvent 12341234::'),
    (re.compile(r'datetime.datetime(.*)'),
     'datetime.datetime(2011, 10, 1, 9, 45)'),
    (re.compile(r"ObjectId\('[0-9a-f]*'\)"),
     "ObjectId('4e7ddf12e138237403000000')"),
    (re.compile(r"object at 0x[0-9a-f]*>"),
     "object at 0x001122>"),
    (re.compile('at 0x[0-9a-f]+'), 
     'at <SOME ADDRESS>'),

    #flexible isoformat T or space
    (re.compile(r"20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])(T| )"\
                 "\d\d:\d\d\:\d\d.[0-9]*Z*"),
     "2011-12-13 07:47:51.921000"),
    #email header
    (re.compile(r"X-Peer: .*"),
     "127.0.0.1:54321"),

    ])

OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS |
               doctest.REPORT_ONLY_FIRST_FAILURE
               #|doctest.REPORT_NDIFF
               )

# MOCK NOW()
# https://gist.github.com/1113164
import contextlib
import datetime


@contextlib.contextmanager
def mock_now(dt_value):
    """Context manager for mocking out datetime.now() in unit tests.

    Example:
    with mock_now(datetime.datetime(2011, 2, 3, 10, 11)):
        assert datetime.datetime.now() == datetime.datetime(2011, 2, 3, 10, 11)

    """

    class MockDateTime(datetime.datetime):
        @classmethod
        def now(cls):
            # Create a copy of dt_value.
            return datetime.datetime(
                dt_value.year, dt_value.month, dt_value.day,
                dt_value.hour, dt_value.minute, dt_value.second,
                dt_value.microsecond, dt_value.tzinfo
            )
    real_datetime = datetime.datetime
    datetime.datetime = MockDateTime
    try:
        yield datetime.datetime
    finally:
        datetime.datetime = real_datetime
