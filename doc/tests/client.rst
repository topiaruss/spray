client tests
============

Let's create the hub that wraps our messaging service, and hides the 
details of making and finding queues.

  >>> from spray import hub
  >>> ourhub = hub.Hub()

Now we request a queue from the hub. It never having been created before  it
will have to be created for the first time. The get_or_create method worries
about such details for us.

  >>> send_queue = ourhub.get_or_create("send")

Now that we have a queue we can associate it with a new source.   
The source from then onwards is our connection to the whole 
messaging system.

  >>> from spray import client
  >>> my_source = client.Source("my_events", send_queue)

We can send events and associated data using the source

TODO: revisit this... out of date...

  >>> crafter_data = dict(name='Russ Ferriday', email='russf@topia.com')
  >>> _=my_source.send("system.project.drafted", crafter_data)


Let's make that simpler
-----------------------

It's a pain if every 'user' of the source needs to understand  the
Hub<->Queue<->Source connection, so we provide a factory for  a source that
creates a queue internally. (Usually the user of the  source does not care
about the queue. Instead, we create the queue internally,  and give it the
name of the source.)

  >>> my_easy_source = client.Source('my_easy_events')
  >>> my_easy_source.send_queue.name
  'my_easy_events'

More often, we *know* that we want to use a shared queue that takes events
from multiple packages/sources. In this case we create a  Source that knows
the name of the queue it will use, but does not need to  create the queue. We
flag this by giving the string name of the queue as the second parameter.

  >>> source_using_shared_queue = client.Source('my_events_to_process', 'send')
  >>> source_using_shared_queue.send_queue.name
  'send'


Providing Data
--------------

In our csv file we use for tests (btw, this is intended to become our production
matrix, so we are not hiding anything...), called 

 System Event-Action matrix - Matrix.csv, 

there is the event_id 'system.project.drafted'. To send that event, I need
to provide the following data::

   crafter_first_name
   project_preview_url
   crafter_email_address

This is an easy case. Later, we'll need to provide perhaps eight fields, and 
that will become quite onerous. Once an event is running and a message is
being sent, if the marketing deparment decides to add a new field to that
message, then the code that's generating events will be one field short
of its data.  Two points here: 1. it is essential that the message 
building not fail if a field is missing.  2. it would be nice if in most
cases, adding a field did not cause any more developer work, and 
in the extreme case, that we were told about any field that could not 
be filled. 

This Section describes how we plan to do all that.

The basic notion is that we can pass a bundle of context to all top-level 
event-sending calls. What is in this bundle will depend on the context
of the call. If we are logged in we can pass either the user id, or
the user object, if we have it to hand.  If we are on a project page
we can pass in the project id, or the project object. If we are also
logged in, we'll pass in the user. If not, we won't ;)

It will be up to the top-level event to turn the information it has into
a field value, if it can.  How can it magically do this? Easy! Read on.


First let's see what field names are in the message for the event.  
We won't normally use this at runtime, but it's handy for development
and this call will be used internally by the client system.

(We'll need a matrix for this...)

  >>> from spray import matrix
  >>> from spray import SPRAY_ROOT
  >>> mm = matrix.CSVActionMatrix(SPRAY_ROOT + '/doc/tests/System Event-Action matrix - Matrix.csv')
  >>> mm.update()

Stripped out some stuff here, since moving to separate assembler class.

  >>> src = client.Source('src', matrix=mm)

Now let's Mock the inside of src, the bit that sends over the wire...

  >>> from mock import MagicMock
  >>> src._send = MagicMock()
  >>> status = src.send('system.project.drafted')
  >>> src._send.assert_called_once_with('system.project.drafted',
  ...     {'site_id': 1})

No magic so far. Without the mock, we would send the event_id, but nothing else.
This is not good for the spray backend, but it will just have to take what it
gets. 

Let's see what's in status
  
  >>> sorted(status['unfilled'])
  ['crafter_email_address', 'crafter_first_name', 'project_preview_url']

So, helpfully, the send method has told us that it was unable to fill three fields.

What do we need to do to help those fields get filled? 

Define Callbacks!!::

  >>> def crafter_email_address_callback(crafter):
  ...     return 'crafty@nevernever.never'
  ...
  >>> crafter_email_address_callback.token_id = 'crafter_email_address'
  ...
  >>> def crafter_first_name_callback(crafter):
  ...     return 'crafty'
  ...
  >>> crafter_first_name_callback.token_id = 'crafter_first_name'
  ...
  >>> def project_preview_url_callback(project):
  ...     return 'sillyproject'
  ...
  >>> project_preview_url_callback.token_id = 'project_preview_url'

  >>> client.register_callback(crafter_email_address_callback)
  >>> client.register_callback(crafter_first_name_callback)
  >>> client.register_callback(project_preview_url_callback)

what did we just cause to happen?

  >>> sorted(client.CALLBACKS.items())
  [('crafter_email_address', <function crafter_email_address_callback at <SOME ADDRESS>>),
   ('crafter_first_name', <function crafter_first_name_callback at <SOME ADDRESS>>),
   ('project_preview_url', <function project_preview_url_callback at <SOME ADDRESS>>)]

Ah. I get it.  So now, if I make the same call again, giving some context...

  >>> src._send = MagicMock()
  >>> project=object()
  >>> context = dict(project=project)
  >>> status = src.send('system.project.drafted', context)
  >>> expect = dict(project_preview_url='sillyproject', site_id=1)
  >>> src._send.assert_called_once_with('system.project.drafted', expect)
  >>> sorted(status['unfilled'])
  []
  >>> sorted(status['no_source'])
  ['crafter']

Status is telling me that it had no source for the crafter.

Oh, so if sender is given a callback, but the source for that callback to do its
job is not available, you tell me the name of the source. 

My god, that's clever.  And if I do it with a full set of context?

  >>> src._send = MagicMock()
  >>> project, crafter = object(), object()  
  >>> context = dict(project=project, crafter=crafter)
  >>> status = src.send('system.project.drafted', context)
  >>> expect = dict(crafter_email_address='crafty@nevernever.never',
  ... crafter_first_name='crafty', project_preview_url='sillyproject',
  ... site_id=1)
  >>> src._send.assert_called_once_with('system.project.drafted', expect)
  >>> sorted(status['unfilled'])
  []

  >>> sorted(status['no_source'])
  []

Let's prove it works when the callbacks are in a separate package. (roger and
kilroy are just printed as evidence that the calls were made.)

  >>> from spray.tests import callbacks
  >>> src._send = MagicMock()
  >>> context = dict(project=project, crafter=crafter)
  >>> status = src.send('system.project.drafted', context)
  <type 'object'>
  roger
  <type 'object'>
  kilroy

  >>> expect = dict(crafter_email_address='crafty@nevernever.never',
  ... crafter_first_name='crafty', project_preview_url='sillyproject',
  ... site_id=1)
  >>> src._send.assert_called_once_with('system.project.drafted', expect)
  >>> sorted(status['unfilled'])
  []

  >>> sorted(status['no_source'])
  []

Now we can fill out all the callbacks for the client, and ensure we pass all relevant 
context when we send events, and we are done ;)

Cool! Ship it!
