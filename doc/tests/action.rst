action and processing
=====================

There will be an action matrix.  Later we may make a nice ZCA interface
for this, but for now let's just assume we go direct to a GoogleDocSpreadsheet

First let's make an event, that we can fake with

  >>> from spray import event
  >>> user_data = dict(name='Kai Diefenbach', email='kai@iqpp.de')
  >>> fake = event.Event('user.profile.register', user_data)

Now lookup the action(s) for the event

  >>> from spray import action 
  >>> my_matrix = action.GoogleActionMatrix(keys, url)
  >>> actions = my_matrix[fake.event_id]
  >>> actions
  [<Action email action>]

And invoke them. (We need a fakeout template for this)

  >>> [a.handle(fake) for a in actions]
  some message ought to print here

Let's make a processor and bind it to the Spreadsheet

  >>> the_processor = action.Processor('send', my_matrix)
  >>> from spray import client
  >>> source = client.Source('fake_events', 'send')
  >>> source.send("user.profile.register", user_data)
  >>> the_processor.step()
  some message here

  















