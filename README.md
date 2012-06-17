Spray
=====

A python system for turning website events into 
e-mail, SMS, or social actions.  

Development status : Pre-Alpha - contributions welcome.

Getting started
---------------

We're developing on Ubuntu 11.04, but OSX and other platforms
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

Docs
----

There's an argoUML file, spray/doc/spray.zargo, containing the 
design that we are working to.

spray/doc/tests contains python doctests that outline how to 
use the code.

TODO
----

+ Wrap an easy-to-install-and-manage local-runnable messaqe queue in the Hub/Queue abstractions. RabbitMQ?

+ Open a path for AEMatrix templates to the templating/output module

+ Write the CommsLog, to ensure that no duplicates are sent

+ Install @yenzenz 's dummy SMTP server under a destination?


