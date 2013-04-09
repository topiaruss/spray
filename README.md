Spray
=====

A python system for turning website events into
e-mail, SMS, or social actions.

Development status : Pre-Alpha - contributions welcome.

Getting started
---------------

We're developing on Ubuntu 11.04, and OSX. Other platforms
should be fine too, given a few tweaks.

If you have not developed on your system before, you may need to do the following::

    $ sudo apt-get install -y build-essential python-dev
    $ sudo apt-get install -y python-virtualenv
    $ sudo apt-get install -y openssh-server

The first one of these commands will ask for your password.

It's good development practice to use a virtual environment for your work.
The following commands will create a top level folder for sponsorcraft
development, then a folder whose job is is to provide the virtualenv::

    $ cd
    $ mkdir sc
    $ cd sc
    $ virtualenv spray
    $ cd spray
    $ source bin/activate

If all that has worked, you should see "(spray)" at the start of the command prompt:
Now you should proceeed by forking this repository at github, using your browser,
then clone it into the current directory on your development machine - something like this::

    $ git clone https://github.com/Sponsorcraft/spray.git

In case you are confused, there will now be ANOTHER directory called spray, in
the current directory that is ALSO called spray.

Assuming the clone worked, issue the following commands::

    $ cd spray
    $ python bootstrap.py -v 1.7.0
    $ bin/buildout
    $ bin/test

Test will probably complain due to lack of credentials files, and a few test
areas will have hardcoded email addresses that need looking at.

You need to have access to an SQS queue, and an SES account on your AWS
account. Then you can start sending  formatted messages, by running bin/sprayd
in the background, and using

    $ bin/client
    or
    $ bin/dryrun -t your.email@wherever.net

to send a single message to the queue.

If sprayd has trouble finding a queue, try running the client first, and then
bin/sprayd in the background.  This will make sure the queue is present
in your account before sprayd tries to attach to it.


Docs
----

There's an argoUML file, spray/doc/spray.zargo, containing the
design that we are working to.

spray/doc/tests contains python doctests that outline how to
use the code.

TODO
----

+ clean up our template -- looks like it was copied from somewhere ;)

+ implement and integrate the CommsLog, to ensure that no duplicates are sent

+ design a stats collection/presentation concept

+ hunt, validate, and eliminate TODOs

