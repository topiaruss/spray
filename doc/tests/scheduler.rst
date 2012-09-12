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

Build a mock database based on our Project requirements that can be accessed
by the accessor we provide, below. This could be an other runtime datasource.

    >>> import datetime
    >>> cd = datetime.datetime(2012, 1, 1, 0, 0)
    >>> dl = datetime.datetime(2013, 1, 1, 0, 0)
    >>> Projects = [dict(id=1, project_submitted=cd, deadline=dl)]
    >>> cd = datetime.datetime(2012, 5, 20, 12, 15)
    >>> dl = datetime.datetime(2012, 8, 20, 12, 15)
    >>> Projects += [dict(id=2, project_submitted=cd, deadline=dl)]

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
  >>> mm = matrix.CSVActionMatrix(
  ...   './doc/tests/System Event-Action matrix - Matrix.csv')
  >>> mm.update()


PeriodicEvent
-------------

The periodic event is instantiated with just enough information to determine
its type and its running schedule. It does not contain all the usual context
information, since that is likely to change over time, and storing it 
for three months in the db is silly. 

Since this event processing will have access to the Event Matrix, we also do
not need to store the period for the event in the event itself. This way, if
the period  changes, spray can adjust on-the-fly.

Let's build an event that is scheduled around the END of the project, and test
the next_occurrence calculation

    >>> from spray.scheduler import PeriodicEvent
    >>> ev = PeriodicEvent(eid='system.project.stats', 
    ...   gov_class='Project', 
    ...   gov_id=1, 
    ...   gov_field='deadline', 
    ...   mm=mm, accessor=dummy_db_access)
    >>> ev
    PeriodicEvent id:'system.project.stats' gov_class:'Project' 
      gov_id:1 gov_field:'deadline'
    
    >>> ev.period(mm)
    datetime.timedelta(-7)

Set the now() time to a couple of weeks before the end of the project

    >>> from spray.utils import ourtime
    >>> ourtime.setnow(datetime.datetime(2012, 12, 16, 0, 0))

Explicitly update the schedule based on the current time. We don't want 
next_occurence to update automatically, because our schedule will be looking 
for items that either have elapsed or will elapse in a certain upcoming time
window.
We don't want next_occurrence to be a Heisenberg quantity ;), so 
schedule_next() updates the internal quantity next_occurence, and 
returns that value, for convenience. The value can be re-read without
it changing.

    >>> ev.schedule_next(mm, dummy_db_access)
    datetime.datetime(2012, 12, 18, 0, 0)

You can see the internal value is accessible, and is the same

    >>> ev.next_occurrence
    datetime.datetime(2012, 12, 18, 0, 0)

Move the clock to just over a week before the end of the project

    >>> ourtime.setnow(datetime.datetime(2012, 12, 19, 0, 0))
    >>> ev.schedule_next(mm, dummy_db_access)
    datetime.datetime(2012, 12, 25, 0, 0)

Finally, set clock to less than a week to the end of the period.
The response to schedule_next() is None, because the event has elapsed.

    >>> ourtime.setnow(datetime.datetime(2012, 12, 26, 0, 0))
    >>> ev.schedule_next(mm, dummy_db_access)

    >>> ourtime.reset()

Now let's start again, with an event that is based on a START time. This time
we'll set the time before creating the event, to prove that the
next_occurrence is updated on creation.

    >>> ourtime.setnow(datetime.datetime(2012, 1, 1, 0, 0))
    >>> ev = PeriodicEvent(eid='system.project.drafted', 
    ...   gov_class='Project', 
    ...   gov_id=1, 
    ...   gov_field='project_submitted', 
    ...   mm=mm, accessor=dummy_db_access)

    >>> ev
    PeriodicEvent id:'system.project.drafted' gov_class:'Project' 
      gov_id:1 gov_field:'project_submitted'
    
    >>> ev.period(mm)
    datetime.timedelta(7)

    >>> ev.next_occurrence
    datetime.datetime(2012, 1, 8, 0, 0)

You can see that even at the same time as the start of the period, the next
occurrence is a  week later, as expected.  You can also see that the next
occurrence was update at  event creation.

If we update the clock to the 7th of January, just before midnight, the next
occurrence  remains the same

    >>> ourtime.setnow(datetime.datetime(2012, 1, 7, 23, 59, 59))
    >>> ev.schedule_next(mm, dummy_db_access)
    datetime.datetime(2012, 1, 8, 0, 0)

but one second later, the next occurrence has been updated to the following
weekly period.

    >>> ourtime.setnow(datetime.datetime(2012, 1, 8, 0, 0))
    >>> ev.schedule_next(mm, dummy_db_access)
    datetime.datetime(2012, 1, 15, 0, 0)

External_nix
------------

Our scheduler does not want to know about the many reasons that an event might
be cancelled, so we pass in a callback, called external_nix.  It is called  at
the start of the schedule_next, with one parameter, the event. If it returns
anything evaluating to True, the next_occurrence is set to None.

Let's try it with a duplicate of the event above, and give it a nix
function that kills the event when the deadline is exceeded.

    >>> def project_nix(event):
    ...     index = event.gov_id
    ...     deadline = [p for p in Projects if p['id'] == index][0]['deadline']
    ...     return ourtime.now() >= deadline

    >>> ourtime.setnow(datetime.datetime(2012, 12, 31, 23, 59, 59))
    >>> from spray.scheduler import PeriodicEvent
    >>> ev = PeriodicEvent(eid='system.project.drafted', 
    ...   gov_class='Project', 
    ...   gov_id=1, 
    ...   gov_field='project_submitted', 
    ...   mm=mm, accessor=dummy_db_access,
    ...    external_nix=project_nix)
    >>> ev.next_occurrence
    datetime.datetime(2013, 1, 6, 0, 0)


This makes sense. If not for the project_nix, the event would recur on the 6th
of January 2013, which is a Sunday, like all other intervals for that event.

So now let's advance time one second, so that we meet the project_nix
condition.

    >>> ourtime.fast_forward(seconds=1)
    >>> from spray.scheduler import PeriodicEvent
    >>> ev = PeriodicEvent(eid='system.project.drafted', 
    ...   gov_class='Project', 
    ...   gov_id=1, 
    ...   gov_field='project_submitted', 
    ...   mm=mm, accessor=dummy_db_access,
    ...    external_nix=project_nix)
    >>> ev.next_occurrence

So that explores both ends of the interval scheduling, the external_nix
method.

Let's check one more thing -- the expiry_date option. For that, we'll use the
same event as before, but adding an expiry date of the first of March, 2012.
We'll look at the next occurrence before and after expiry.

    >>> ourtime.setnow(datetime.datetime(2012, 2, 29, 23, 59, 59))
    >>> expdate = datetime.datetime(2012, 3, 1, 0, 0)
    >>> from spray.scheduler import PeriodicEvent
    >>> ev = PeriodicEvent(eid='system.project.drafted', 
    ...   gov_class='Project', 
    ...   gov_id=1, 
    ...   gov_field='project_submitted', 
    ...   mm=mm, accessor=dummy_db_access,
    ...    expiry_date=expdate)

    >>> ev.next_occurrence
    datetime.datetime(2012, 3, 4, 0, 0)

Creep forward one second

    >>> ourtime.fast_forward(seconds=1)
    >>> ev.schedule_next(mm, dummy_db_access)
    >>> ev.next_occurrence

Here's the calender for 2012::

                                 2012

          January               February               March
    Su Mo Tu We Th Fr Sa  Su Mo Tu We Th Fr Sa  Su Mo Tu We Th Fr Sa
     1  2  3  4  5  6  7            1  2  3  4               1  2  3
     8  9 10 11 12 13 14   5  6  7  8  9 10 11   4  5  6  7  8  9 10
    15 16 17 18 19 20 21  12 13 14 15 16 17 18  11 12 13 14 15 16 17
    22 23 24 25 26 27 28  19 20 21 22 23 24 25  18 19 20 21 22 23 24
    29 30 31              26 27 28 29           25 26 27 28 29 30 31
                                                
           April                  May                   June
    Su Mo Tu We Th Fr Sa  Su Mo Tu We Th Fr Sa  Su Mo Tu We Th Fr Sa
     1  2  3  4  5  6  7         1  2  3  4  5                  1  2
     8  9 10 11 12 13 14   6  7  8  9 10 11 12   3  4  5  6  7  8  9
    15 16 17 18 19 20 21  13 14 15 16 17 18 19  10 11 12 13 14 15 16
    22 23 24 25 26 27 28  20 21 22 23 24 25 26  17 18 19 20 21 22 23
    29 30                 27 28 29 30 31        24 25 26 27 28 29 30
                                                
            July                 August              September
    Su Mo Tu We Th Fr Sa  Su Mo Tu We Th Fr Sa  Su Mo Tu We Th Fr Sa
     1  2  3  4  5  6  7            1  2  3  4                     1
     8  9 10 11 12 13 14   5  6  7  8  9 10 11   2  3  4  5  6  7  8
    15 16 17 18 19 20 21  12 13 14 15 16 17 18   9 10 11 12 13 14 15
    22 23 24 25 26 27 28  19 20 21 22 23 24 25  16 17 18 19 20 21 22
    29 30 31              26 27 28 29 30 31     23 24 25 26 27 28 29
                                                30
          October               November              December
    Su Mo Tu We Th Fr Sa  Su Mo Tu We Th Fr Sa  Su Mo Tu We Th Fr Sa
        1  2  3  4  5  6               1  2  3                     1
     7  8  9 10 11 12 13   4  5  6  7  8  9 10   2  3  4  5  6  7  8
    14 15 16 17 18 19 20  11 12 13 14 15 16 17   9 10 11 12 13 14 15
    21 22 23 24 25 26 27  18 19 20 21 22 23 24  16 17 18 19 20 21 22
    28 29 30 31           25 26 27 28 29 30     23 24 25 26 27 28 29
                                                30 31












