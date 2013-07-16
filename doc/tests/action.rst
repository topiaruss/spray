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

  >>> from spray import matrix
  >>> from spray import SPRAY_ROOT
  >>> mm = matrix.CSVActionMatrix(SPRAY_ROOT + '/doc/tests/System Event-Action matrix - Matrix.csv')

We must call update anytime the datasource may have changed.  This is the case
irrespective which type of ActionMatrix we use.

  >>> mm.update()

Just to demonstrate how the matrix works, we'll use it to look up the
action(s) for our fake event, and check the type of the first one

  >>> actions = mm.get_actions(fake)
  >>> actions[0].action_type
  'EmailAction'

Hmmm... That's the normal email action. Let's replace it with the
Dummy Handler

  >>> from spray import action
  >>> action.ACTIONS['email'] = action.AVAILABLE_ACTIONS['DummyEmailAction']

Check

  >>> actions = mm.get_actions(fake)
  >>> actions[0].action_type
  'DummyEmailAction'

Now let's invoke the handler(s) for the event. The current
DummyEmailAction just prints some info, as you'll see below

  >>> [a.handle() for a in actions]
    {   'action_type': u'email',
        'event_id': u'user.profile.register',
        'recipient': u'admins'}
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

  >>> the_processor = action.Processor('send', mm, running=False)
  >>> the_processor
  <spray.action.Processor object at ...>

Now let's create a dummy source named 'fake_events', 'cause that's all it does.
It will explicitly use the 'send' queue.

  >>> from spray import client
  >>> source = client.Source('fake_events', 'send')

Let's send something into the queue using this source

  >>> _=source.send("system.project.drafted", user_data)

And do a single step on the processor to see what it does.

  >>> the_processor.step()
    {   'action_type': u'email',
        'event_id': u'system.project.drafted',
        'recipient': u'crafter'}
    {   'email': 'russf@topia.com', 'name': 'Russ Ferriday', 'site_id': 1}


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

  >>> creds = matrix.Credentials()

Now we can proceed and get the demo spreadsheet. Bear in mind this goes to Google
for data, so it stretches your tests a bit.  If you find this block commented out
with ".." you know why...

Testing Matrix

  .. >>> url = 'https://docs.google.com/a/sponsorcraft.com/spreadsheet/ccc?key=0AgfJ64xPw-46dG9ITmowOEhQNU85c2NhOUtsb2ZzbFE'

Production Matrix

  .. >>> url = 'https://docs.google.com/a/sponsorcraft.com/spreadsheet/ccc?key=0AoY07RiDm5HYdDR6R2hiSVE4aWI1azlMYlRnZlhSSVE#gid=0'

  Development Matrix
  >>> url = 'https://docs.google.com/a/sponsorcraft.com/spreadsheet/ccc?key=0AgfJ64xPw-46dE13Vk5ydFJFcTBJOFBYbmlBc2ROenc'

  >>> mm = matrix.GoogleActionMatrix(creds, url)
  >>> mm.update()

Now we just repeat the code above to test that the Google matrix works just the same
as the CSV matrix

  >>> the_processor = action.Processor('send', mm, running=False)
  >>> source = client.Source('fake_events', 'send')
  >>> ret = source.send("user.profile.register", user_data)
  >>> ret == {'unfilled': [], 'no_source': [], 'results': {}}
  True

  >>> step = the_processor.step()
    {   'action_type': 'email',
        'event_id': 'system.project.drafted',
        'recipient': 'crafter'}
    {   'email': 'kai@iqpp.de', 'name': 'Kai Diefenbach', 'site_id': 1}









