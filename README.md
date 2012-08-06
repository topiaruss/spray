Spray
=====

A python system for turning website events into 
e-mail, SMS, or social actions.  

Development status : Pre-Alpha - contributions welcome.

Getting started
---------------

We're developing on Ubuntu 11.04, and OSX. Other platforms
should be fine too, given a few tweaks.

Start by forking this repository, then clone it to your development
machine - something like this::

    $ git clone https://github.com/Sponsorcraft/spray.git

Issue the following commands::

    $ cd spray
    $ virtualenv .
    $ source bin/activate
    $ python bootstrap.py 
    $ bin/buildout 
    $ bin/test

Test will probably complain due to lack of credentials files, and a few test
areas will have hardcoded email addresses that need looking at.

Once you have access to an SQS queue, and an SES account, you can start sending 
formatted messages, by running bin/sprayd, and using bin/client to send a single
message to the queue.

Docs
----

There's an argoUML file, spray/doc/spray.zargo, containing the 
design that we are working to.

spray/doc/tests contains python doctests that outline how to 
use the code.

TODO
----

+ extend the client side, to make it easier to generate our 
  events and fill them with data.

+ clean up our template -- looks like it was copied from somewhere

+ implement and integrate the CommsLog, to ensure that no duplicates are sent

+ design a stats collection/presentation concept

+ hunt, validate, and eliminate TODOs

