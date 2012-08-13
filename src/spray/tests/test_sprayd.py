
from spray import sprayd
import unittest



class TestSprayd(unittest.TestCase):

    def test_instance(self):
        app = sprayd.app(testing=True)
        app = app  # fake-out syntax checker
