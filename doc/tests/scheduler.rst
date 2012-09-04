Scheduler
=========

This follows the outline in the ArgoUML file under the Scheduler package.

Below we define a flexible scheduler that is able to source repeats of an
event.

Coupled with the other parts of Spray, it allows us to generate messages
on a flexible schedule, counting up from, or down to specific times

The main components of the subsystem are the PeriodicEvent, and the
PeriodicEventQ.

The PeriodicEventQ contains no persistent data. All relevant data are
contained in instances of PeriodicEvent. So a single-table 
implementation in SQL is obvious.

Working Data
------------

Build a mock database that can be accessed by the accessor we provide.

    >>> import datetime
    >>> cd = datetime.datetime(2012, 1, 1, 0, 0)
    >>> dl = datetime.datetime(2013, 1, 1, 0, 0)
    >>> Projects = [dict(id=1, create_date=cd, deadline=dl)]
    >>> cd = datetime.datetime(2012, 5, 20, 12, 15)
    >>> dl = datetime.datetime(2012, 8, 20, 12, 15)
    >>> Projects += [dict(id=2, create_date=cd, deadline=dl)]

And then the accessor
    >>> def dummy_db_access(table, index, field):
    ...     "access a project field by index and field name"
    ...     assert table == 'Project'
    ...     match = [p for p in Projects if p['id'] == index]
    ...     return match and match[0][field] or None
    ...

Action Matrix
-------------

  >>> from spray import matrix 
  >>> mm = matrix.CSVActionMatrix('./doc/tests/System Event-Action matrix - Matrix.csv')
  >>> mm.update()

Monkey Patch time
-----------------

Test our mocking Fu

    >>> from spray.testing import mock_now
    >>> with mock_now(datetime.datetime(2011, 2, 3, 10, 11)):
    ...     assert datetime.datetime.now() == datetime.datetime(2011, 2, 3, 10, 11)
    ...     assert datetime.datetime.now() == datetime.datetime(2011, 2, 3, 10, 11)

PeriodicEvent
-------------

The periodic event is instantiated with just enough information to determine
its type and its running schedule. It does not contain all the usual context
information, since that is likely to change over time, and storing it 
for three months in the db is silly. 

Since this event processing will have access to the Event Matrix, we also do not need
to store the period for the event in the event itself. This way, if the period 
changes, spray can adjust on-the-fly.

    >>> from spray.scheduler import PeriodicEvent
    >>> ev = PeriodicEvent('system.project.stats', 'Project', 1, 'deadline', mm=mm, accessor=dummy_db_access)
    >>> ev
    PeriodicEvent id:'system.project.stats' gov_class:'Project' gov_id:1 gov_field:'deadline'
    
    >>> ev.period()
    datetime.timedelta(-7)

    >>> with mock_now(datetime.datetime(2012, 12, 15, 0, 0)):
    ...     ev = PeriodicEvent('system.project.stats', 'Project', 1, 'deadline', mm=mm, accessor=dummy_db_access)
    ...     ev.next_occurrence
    datetime.datetime(2012, 12, 22, 0, 0)

    >>> with mock_now(datetime.datetime(2012, 12, 23, 0, 0)):
    ...     ev = PeriodicEvent('system.project.stats', 'Project', 1, 'deadline', mm=mm, accessor=dummy_db_access)
    ...     ev.next_occurrence
    datetime.datetime(2012, 12, 31, 0, 0)

