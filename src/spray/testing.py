import doctest
import re
from zope.testing import renormalizing

checker = renormalizing.RENormalizing([
    (re.compile(r'i-[0-9a-f]*'),
     'i-66699942'),
    (re.compile(r'datetime.datetime(.*)'),
     'datetime.datetime(2011, 10, 1, 9, 45)'),
    (re.compile(r"ObjectId\('[0-9a-f]*'\)"),
     "ObjectId('4e7ddf12e138237403000000')"),
    (re.compile(r"object at 0x[0-9a-f]*>"),
     "object at 0x001122>"),
    #flexible isoformat T or space
    (re.compile(r"20\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])(T| )"\
                 "\d\d:\d\d\:\d\d.[0-9]*Z*"),
     "2011-12-13 07:47:51.921000"),
    ])

OPTIONFLAGS = (doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS |
               doctest.REPORT_ONLY_FIRST_FAILURE
               #|doctest.REPORT_NDIFF
               )
