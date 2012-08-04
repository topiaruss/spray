from spray.utils import observer
import unittest


def obs1(e):
    assert e.a == 42


def doomwatch(e):
    assert e.message == 'time flies'
    assert 'devil' in e.source.details
    assert e.source.trouble == 666

# First Pair to Mix


class SomeParent(observer.Observable):
    "just for testing"
    def __init__(self):
        super(SomeParent, self).__init__()
        self.details = 'devil'


class ObservableInherited(SomeParent):

    def __init__(self):
        super(ObservableInherited, self).__init__()
        self.trouble = 666


class TestObserverInherited(unittest.TestCase):

    def test_observer_creation(self):
        obs = observer.Observable()
        obs = obs  # defeat checker

    def test_observer_notification(self):
        obs = observer.Observable()
        obs.subscribe(obs1)
        obs.notify(a=42)

    def test_observer_inherited(self):
        mixed = ObservableInherited()
        mixed.subscribe(doomwatch)
        mixed.notify(message='time flies')


# Second Pair to mix

class SomeSilliness(object):

    def __init__(self):
        super(SomeSilliness, self).__init__()
        self.silly = 1


class ObservableSilliness(SomeSilliness, observer.Observable):

    def __init__(self):
        super(ObservableSilliness, self).__init__()
        self.foo = 'bar'


def silly(e):
    assert e.message == 'wahoo!'
    assert e.source.silly == 1
    assert e.source.foo == 'bar'


class TestObserverMixed(unittest.TestCase):

    def test_observer_mixable(self):
        mixed = ObservableSilliness()
        mixed.subscribe(silly)
        mixed.notify(message='wahoo!')
