action and processing
=====================

There will be an action matrix.  Later we may make a nice ZCA interface
for this, but for now let's just assume we go direct to a GoogleDocSpreadsheet


First let's make an event to use for testing

  >>> from spray import event
  >>> user_data = dict(name='Kai Diefenbach', email='kai@iqpp.de')
  >>> fake = event.Event('user.profile.register', user_data)



Great, but we also have a CSVActionMatrix, let's test it for a moment..
  >>> from spray import action 
  >>> matrix = action.CSVActionMatrix('./doc/tests/Extract of System Event-Action matrix - Matrix.csv')
  >>> matrix.update()

Now use it to look up the action(s) for the event

  >>> actions = matrix.get_actions(fake)
  >>> actions[0].action_type
  'email'





  .. >>> from spray import action 
  .. >>> creds = action.Credentials()
  .. >>> url = 'https://docs.google.com/a/sponsorcraft.com/spreadsheet/ccc?key=0AgfJ64xPw-46dENnMWQwM2dOTTNaZWo3M1JZOEtVa1E'
  .. >>> my_matrix = action.GoogleActionMatrix(creds, url)
  .. >>> my_matrix.update()
  .. >>> actions = my_matrix.get_actions(fake)
  .. >>> actions[0].action_type
  .. 'email'

And invoke them. 

  >>> [a.handle() for a in actions]
  action: email data: {'email': 'kai@iqpp.de', 'name': 'Kai Diefenbach'}.
  [None]


Let's make a step-by-step processor that watches the send queue, and is 
controlled by the Spreadsheet

  >>> the_processor = action.Processor('send', matrix, running=False)

Now let's create a dummy source named 'fake_events', 'cause that's what it does

  >>> from spray import client
  >>> source = client.Source('fake_events', 'send')

Let's send something using that source into the queue

  >>> source.send("user.profile.register", user_data)

And do a single step on the processor to see what it does.

  >>> the_processor.step()
  processed step

















