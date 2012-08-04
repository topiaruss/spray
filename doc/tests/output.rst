Output
======

Building a template registry as a pre-req
-----------------------------------------

** Note that we are using a very simple template for this doc. The model we
will use  for spray messaging will have two levels of templating. One level
where we  take the text defined in the spreadsheet as our template and insert
data. You could  call that "content templating". And the other level which has
more to do with graphic layout. You could call that "layout templating".  The
templating that's happening in these docs is effectively a mixture of both.

  >>> from spray import output
  >>> reg = output.TemplateRegistry()

Register a default template. The key for a default template is always ''.

  >>> reg.register('', 'Hello {{ name }}!')

We can use the registry's convenience method, so we don't need to access the
template object directly

  >>> reg.render(dict(name='John'))
  u'Hello John!'

Let's add a longer template, and test it

  >>> reg.register('longer', 'Hello {{ name }}! You are a valued friend!')
  >>> reg.render(dict(name='John'), style='longer')
  u'Hello John! You are a valued friend!' 


Looking up an output channel
----------------------------

There is a ChannelRegistry Class, from which Channels can be 
looked up. There also a registry in the OUTPUT module that
contains all the normally provided channels. See later, for that

  >>> chan_reg = output.ChannelRegistry()

If you try to lookup a channel that does not exist you'll
receive a KeyError

  >>> chan = chan_reg.lookup('dummy_email')
  Traceback (most recent call last):
    ...
  KeyError: 'dummy_email'

Clearly, before we can lookup a channel, there has to be a channel of that
name. So let's create a Channel, giving it a DummyDestination that prints to
stdout.

  >>> emailchan = output.Channel('dummy_email', reg, output.DummyDestination())
  >>> chan_reg.register(emailchan)

Note, above, how we pass the whole channel, and let the registry directly
access the medium and use the key (medium) for its  internal indexing.

Now we use the medium ('dummy_email') to lookup the channel we want to send on.

  >>> got_chan = chan_reg.lookup('dummy_email')
  >>> got_chan.medium
  'dummy_email'

So now we can send on it, using the default style, just by passing
a dict with the data.  The template details are hidden by the Channel!

  >>> got_chan.send(dict(name='John'))
  Hello John!

And we can send using the longer template, very simply

  >>> got_chan.send(dict(name='John'), style='longer')
  Hello John! You are a valued friend!


Moving to SMTP
--------------

Let's take a further step. Let's rebind emailchan to the
mock SMTP destination, and bring the real smtp client into the picture.

  >>> from spray.utils import mocksmtp  # make sure the mock server is running

  >>> dest = output.MockSmtpDestination('127.0.0.1', 9025)
  >>> emailchan = output.Channel('email', reg, dest)
  >>> chan_reg.register(emailchan)
  >>> got_chan = chan_reg.lookup('email')
  >>> data = {'name': 'John', 'from': 'russf@topia.com', 'to': ['russf@topia.com']}
  >>> got_chan.send(data)

  >>> msg = mocksmtp.queue.get()
  >>> print msg.as_string()
  From: russf@topia.com
  To: russf@topia.com
  X-Peer: 127.0.0.1:51088
  X-MailFrom: russf@topia.com
  X-RcptTo: russf@topia.com
  <BLANKLINE>
  Hello John!

And let's send the same data through the same channel, with the longer template

  >>> got_chan.send(data, style='longer')
  >>> msg = mocksmtp.queue.get()
  >>> print msg.as_string()
  From: russf@topia.com
  To: russf@topia.com
  X-Peer: 127.0.0.1:51088
  X-MailFrom: russf@topia.com
  X-RcptTo: russf@topia.com
  <BLANKLINE>
  Hello John! You are a valued friend!

And shorter template, and some headers

  >>> data['headers'] = dict(NoSuch='Header', SomeOther='NonHeader')
  >>> got_chan.send(data)
  >>> msg = mocksmtp.queue.get()
  >>> print msg.as_string()
  From: russf@topia.com
  To: russf@topia.com
  NoSuch: Header
  SomeOther: NonHeader
  127.0.0.1:54321
  X-MailFrom: russf@topia.com
  X-RcptTo: russf@topia.com
  <BLANKLINE>
  Hello John!


Close down the mock
-------------------

  >>> mocksmtp.controller.stop()








