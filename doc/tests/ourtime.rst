Ourtime Package
---------------

Simplifies time/date testing

Important that we use ourtime.now() and ourtime.date() for all time related
work, internally and in tests.

  >>> from spray.utils import ourtime
  >>> start = ourtime.now()
  >>> assert start.year >= 2012

Now let's turn the clock back to 9/11.  We can safely import the datetime
as long as we don't access its now() or date(). In fact we need to use
datetime.datetime() to initialize the fake time.

  >>> import datetime
  >>> ourtime.setnow(datetime.datetime(2001, 9, 11, 16, 0))
  >>> assert ourtime.now().year == 2001

Note that date comes along with the time, very nicely.

  >>> assert ourtime.today().year == 2001

Beware! It's VERY Important to set our time ticking again, once a test has completed

  >>> ourtime.reset()

Let's check it worked

  >>> assert ourtime.now().year >= 2012

Notes:

  * in all our modules, now() and date() should be qualified by the ourtime package


