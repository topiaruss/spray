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

Now that we have a queue we can associate it with a new source.   The source
from then onwards is our connection to the whole messaging system.

  >>> from spray import client
  >>> my_source = client.Source("my_events", send_queue)

We can send events and associated data using the source

  >>> crafter_data = dict(name='Russ Ferriday', email='russf@topia.com')
  >>> my_source.send("system.project.created", crafter_data)


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











