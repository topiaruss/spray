import unittest

from spray import event
from spray import testing


class TestEvent(unittest.TestCase):

    def test_name_attr(self):
        bob = dict(name='bob', email='bob@gmail.com')
        evid = 'user.account.created'
        ev = event.Event(evid, bob)
        assert ev.event_id == evid

    def test_data_attr(self):
        bob = dict(name='bob', email='bob@gmail.com')
        evid = 'user.account.created'
        ev = event.Event(evid, bob)
        assert ev.data == bob

    def test_repr(self):
        bob = dict(name='bob', email='bob@gmail.com')
        evid = 'user.account.created'
        ev = event.Event(evid, bob)
        got = repr(ev)
        want = "<Event 12341234:: event_id user.account.created, " +\
               "datakeys ['email', 'name']>"
        assert testing.checker.check_output(want, got, 0)

    def test_unicode(self):
        bob = dict(name='bob', email='bob@gmail.com')
        evid = 'user.account.created'
        ev = event.Event(evid, bob)
        got = unicode(ev)
        want = "<Event event_id user.account.created, " +\
               "datakeys ['email', 'name']>"
        assert testing.checker.check_output(want, got, 0)

class TestSQSEvent(unittest.TestCase):

    def test_name_attr(self):
        bob = dict(name='bob', email='bob@gmail.com')
        evid = 'user.account.created'
        ev = event.SQSEvent(event_id=evid, data=bob)
        assert ev.event_id == evid

    def test_data_attr(self):
        bob = dict(name='bob', email='bob@gmail.com')
        evid = 'user.account.created'
        ev = event.SQSEvent(event_id=evid, data=bob)
        assert ev.data == bob

    def test_repr(self):
        bob = dict(name='bob', email='bob@gmail.com')
        evid = 'user.account.created'
        ev = event.SQSEvent(event_id=evid, data=bob)
        got = repr(ev)
        want = "<SQSEvent 12341234:: event_id user.account.created, " +\
               "datakeys ['email', 'name']>"
        assert testing.checker.check_output(want, got, 0)

    def test_unicode(self):
        bob = dict(name='bob', email='bob@gmail.com')
        evid = 'user.account.created'
        ev = event.SQSEvent(event_id=evid, data=bob)
        got = unicode(ev)
        want = u"<SQSEvent event_id user.account.created, " +\
               "datakeys ['email', 'name']>"
        assert testing.checker.check_output(want, got, 0)


if __name__ == '__main__':
    unittest.main()
