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
  >>> creds = action.Credentials()
  >>> url = 'https://docs.google.com/a/sponsorcraft.com/spreadsheet/ccc?key=0AgfJ64xPw-46dENnMWQwM2dOTTNaZWo3M1JZOEtVa1E'
  >>> my_matrix = action.GoogleActionMatrix(creds, url)
  >>> my_matrix.update()
  >>> actions = my_matrix.get_actions(fake)
  >>> actions[0].action_type
  'email'

And invoke them. 

  >>> [a.handle() for a in actions]
  action: email data: {'email': 'kai@iqpp.de', 'name': 'Kai Diefenbach'}.
  [None]

Great, but we also have a CSVActionMatrix, let's test it for a moment..

  >>> csv_matrix = action.CSVActionMatrix('./doc/tests/Extract of System Event-Action matrix - Matrix.csv')
  >>> csv_matrix.update()

Let's make a processor and bind it to the Spreadsheet

  >>> the_processor = action.Processor('send', my_matrix)
  >>> from spray import client
  >>> source = client.Source('fake_events', 'send')
  >>> source.send("user.profile.register", user_data)
  >>> the_processor.step()
  some message here

















