hub
===

Let's get or instantiate the send queue

  >>> from spray import hub
  >>> our_hub = hub.Hub()
  >>> sendq = our_hub.get_or_create('send')

And then put an event into it

  >>> from spray import event
  >>> ev = event.Event('id', dict())
  >>> sendq.put_event(ev)
  >>> got = sendq.get_event()
  >>> ev == got
  True 

Let's try the convenience method

  >>> sendq.create_and_send('some.id')
  >>> got = sendq.get_event()
  >>> got.name == 'some.id'
  True