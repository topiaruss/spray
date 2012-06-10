"""Doc Tests"""
import doctest
import itertools
import unittest
from spray import testing


def test_suite():

    tests = (
        doctest.DocFileSuite(
            '../../../doc/tests/hub.rst',
    #        setUp=testing.setUp, tearDown=testing.tearDown,
            checker=testing.checker,
            optionflags=testing.OPTIONFLAGS
            ),

        doctest.DocFileSuite(
            '../../../doc/tests/client.rst',
    #        setUp=testing.setUp, tearDown=testing.tearDown,
            checker=testing.checker,
            optionflags=testing.OPTIONFLAGS
            ),

        doctest.DocFileSuite(
            '../../../doc/tests/action.rst',
    #        setUp=testing.setUp, tearDown=testing.tearDown,
            checker=testing.checker,
            optionflags=testing.OPTIONFLAGS
            )
        )
    return unittest.TestSuite(itertools.chain(*tests))


