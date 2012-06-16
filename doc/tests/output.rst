Output
======

Building a template registry as a pre-req
-----------------------------------------

  >>> from spray import output
  >>> reg = output.TemplateRegistry()
  >>> reg.register('', 'Hello {{ name }}!')
  >>> reg.render(dict(name='John'))
  u'Hello John!'


Looking up an output channel
----------------------------

There is a ChannelRegistry Class, from which Channels can be 
looked up. There also a registry in the OUTPUT module that
contains all the normally provided channels. See later, for that

  >>> chan_reg = output.ChannelRegistry()

If you try to lookup a channel that does not exist you'll
receive a KeyError

  >>> chan = chan_reg.lookup('email')
  Traceback (most recent call last):
    ...
  KeyError: 'email'

Clearly, before we can lookup a channel, there has to be a channel
of that name. 

  >>> emailchan = output.Channel('email', reg, output.DummyDestination())
  >>> chan_reg.register(emailchan)

Note, above, how we pass the whole channel, and let the
registry select the medium for indexing.

Now we use the medium ('email') to lookup the channel we want to send on.

  >>> got_chan = chan_reg.lookup('email')
  >>> got_chan.medium
  'email'

So now we can send on it, using the default style, just by passing
a dict with the data.

  >>> got_chan.send(dict(name='John'))
  Hello John!
