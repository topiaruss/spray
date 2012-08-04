from spray.utils import observer
import unittest

class TestDummyQueue(unittest.TestCase):

    def test_observer_creation(self):
        obs = observer.Observable()

