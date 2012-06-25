from lazr.smtptest.controller import Controller
from lazr.smtptest.server import Server
from Queue import Queue

queue = Queue()

class MockSmtp(Server):
    def handle_message(self, message):
        queue.put(message)

controller = Controller(MockSmtp('127.0.0.1', 9025))
controller.start()
