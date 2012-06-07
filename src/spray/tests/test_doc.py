"""Doc Tests"""
import doctest
from spray import testing


def test_suite():
    return doctest.DocFileSuite(
        '../../../doc/tests/client.rst',
#        setUp=testing.setUp, tearDown=testing.tearDown,
        checker=testing.checker,
        optionflags=testing.OPTIONFLAGS
        )
