Output
======

There is a ChannelRegistry Class, from which Channels can be 
looked up. There also a registry in the OUTPUT module that
contains all the normally provided channels. See later, for that

  >>> from spray import output
  >>> chan_reg = output.ChannelRegistry()

If you try to lookup a channel that does not exist you'll
receive a KeyError

  >>> chan = chan_reg.lookup('email')
  Traceback (most recent call last):
    ...
  KeyError: 'email'

Clearly, before we can lookup a channel, there has to be a channel
of that name. 

  >>> emailchan = output.Channel('email', output.TemplateRegistry)
  >>> chan_reg.register(emailchan)
  >>> got_chan = chan_reg.lookup('email')
  >>> got_chan.medium
  'email'