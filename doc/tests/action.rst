action and processing
=====================

First let's make an event to use for testing.  We'll use the 
kind of event generated when a user joins the site. It
needs some additional data, so that the processor that receives 
the event knows what the event is referring to

  >>> from spray import event
  >>> user_data = dict(name='Kai Diefenbach', email='kai@iqpp.de')
  >>> fake = event.Event('user.profile.register', user_data)

Before we can create a processor, we create a CSVActionMatrix which 
the processor can use to decide what to do when an event arrives.
For testing, we use a canned file to initialize the matrix.

  >>> from spray import action 
  >>> matrix = action.CSVActionMatrix('./doc/tests/System Event-Action matrix - Matrix.csv')

We must call update anytime the datasource may have changed.  This is the case
irrespective which type of ActionMatrix we use.

  >>> matrix.update()

Just to demonstrate how the matrix works, we'll use it to look up the 
action(s) for our fake event, and check the type of the first one

  >>> actions = matrix.get_actions(fake)
  >>> actions[0].action_type
  'EmailAction'

Hmmm... That's the normal email action. Let's replace it with the 
Dummy Handler 

  >>> action.ACTIONS['email'] = action.AVAILABLE_ACTIONS['DummyEmailAction']

Check

  >>> actions = matrix.get_actions(fake)
  >>> actions[0].action_type
  'DummyEmailAction'

Now let's invoke the handler(s) for the event. The current 
DummyEmailAction just prints some info, as you'll see below

  >>> [a.handle() for a in actions]
  {   u'action type': u'email',
      u'body_en_uk': u'',
      u'body_fmt': u'',
      u'frequency': u'',
      u'lag_time': u'',
      u'notes': u'',
      u'recipient': u'crafter',
      u'subject_en_uk': u'',
      u'time of day': u'',
      u'until': u''}
  {   'email': 'kai@iqpp.de', 'name': 'Kai Diefenbach'}
  [None]

What we did above, handling the lookup of action based on event, is not
something that the users of our system will normally do. Instead, we 
have the notion of a processor that binds to the Event Action Matrix and 
does the lookup internally.

So, let's make a step-by-step processor that watches the send queue, and is 
controlled by the Spreadsheet. A step-by-step processor is just a processor 
that needs to be told to process a new event. This is useful for testing.
We create this kind of processor by setting running=False on creation.

  >>> the_processor = action.Processor('send', matrix, running=False)

Now let's create a dummy source named 'fake_events', 'cause that's all it does.
It will explicitly use the 'send' queue.

  >>> from spray import client
  >>> source = client.Source('fake_events', 'send')

Let's send something into the queue using this source

  >>> source.send("system.project.created", user_data)

And do a single step on the processor to see what it does.  

  >>> the_processor.step()
    {   u'action type': u'email',
        u'body_en_uk': u'Dear {{crafter_first_name}},\\n\\nThank you for starting a project on Sponsorcraft. You can view your project at {{project_preview_url}}.\\n\\nAfter submitting your project, our moderation team will review your project and reply with feedback within 1 working day.\\n\\nYour friendly Sponsorcraft website robot.\\n\\n\u2014\\nFor advice and tips on crafting an awesome project, visit http://sponsorcraft.com/college/\\n\\n [[Edit your project]]',
        u'body_fmt': u'',
        u'frequency': u'1w',
        u'lag_time': u'1d',
        u'notes': u'Only send one reminder per crafter! Username if no first_name, last name.',
        u'recipient': u'crafter',
        u'subject_en_uk': u'Your draft project',
        u'time of day': u'',
        u'until': u'project submitted'}
    {   'email': 'russf@topia.com', 'name': 'Russ Ferriday'}


GoogleActionMatrix
==================

Let's show off the more exotic GoogleActionMatrix. This is like the CSV action
matrix, but wraps an online spreadsheet that can be modified by the marketing team
in quasi-real-time.

We need the credentials for any Google Account.  You could either edit the 
"creds =" line to add (email='<YourEmail>', password='<YourPass>'). This
brings the risk that you will commit changes including your password.

The better option is to put them in a two line file under the package directory with::

  YourGoogleAccountName
  YourGoogleAccountPass

and this will be picked up automagically. There is a credentials.txt.template 
file to make it quite clear where the credentials file needs to be installed.  You 
can modify and rename the template file to credentials.txt as you wish.

  >>> creds = action.Credentials()

Now we can proceed and get the demo spreadsheet. Bear in mind this goes to Google
for data, so it stretches your tests a bit.  If you find this block commented out
with ".." you know why...

..   >>> url = 'https://docs.google.com/a/sponsorcraft.com/spreadsheet/ccc?key=0AgfJ64xPw-46dENnMWQwM2dOTTNaZWo3M1JZOEtVa1E'

..   >>> matrix = action.GoogleActionMatrix(creds, url)
..   >>> matrix.update()

.. Now we just repeat the code above to test that the Google matrix works just the same
.. as the CSV matrix

..   >>> the_processor = action.Processor('send', matrix, running=False)
..   >>> source = client.Source('fake_events', 'send')
..   >>> source.send("user.profile.register", user_data)
..   >>> the_processor.step()
..   action: email, data: {'email': 'kai@iqpp.de', 'name': 'Kai Diefenbach'}.
..   {   'action type': 'email',
..       'body_en_uk': u'Dear {crafter_first_name},\\n\\nThank you for starting a project on Sponsorcraft. You can view your project at {project_preview_url}.\\n\\nAfter submitting your project, our moderation team will review your project and reply with feedback within 1 working day.\\n\\nYour friendly Sponsorcraft website robot.\\n\\n\u2014\\nFor advice and tips on crafting an awesome project, visit http://sponsorcraft.com/college/\\n\\n [[Edit your project]]',
..       'frequency': '1w',
..       'lag_time': '1d',
..       'notes': 'Send weekly after one week. Username if no first_name, last name.',
..       'recipient': 'crafter',
..       'subject_en_uk': 'Project reminder',
..       'until': 'project submitted'}
..   processed step









