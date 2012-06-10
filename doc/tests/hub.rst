hub
===

Let's get or instantiate the send queue

  >>> from spray import hub
  >>> sendq = hub.get_or_create('send')

And then put an event into it

  >>> from spray import event
  >>> ev = event.Event('id', dict())
  >>> sendq.putEvent(ev)
  >>> got = sendq.getEvent()
  >>> ev == got
  True 