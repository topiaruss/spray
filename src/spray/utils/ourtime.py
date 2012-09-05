"""Use globally to replace all now() and today() references
to facilitate thorough testing.
Based on Barry Warsaw's package from years ago, with
changes to make this fit my brain better.
--r.
Ref:
http://www.artima.com/weblogs/viewpost.jsp?thread=251755
"""
import datetime


class DateFactory:
    """A factory for today() and now() that works with testing."""

    # Set to True to produce predictable dates and times.
    testing_mode = False
    # The predictable time.
    predictable_now = None
    predictable_today = None

    def now(self, tz=None):
        return (self.predictable_now
                if self.testing_mode
                else datetime.datetime.now(tz))

    def today(self):
        return (self.predictable_today
                if self.testing_mode
                else datetime.date.today())

    @classmethod
    def setnow(cls, set_to=None):
        if set_to is None:
            set_to = datetime.datetime(2012, 7, 26, 0, 0)
        cls.predictable_now = set_to
        cls.predictable_today = cls.predictable_now.date()
        cls.testing_mode = True

    @classmethod
    def reset(cls):
        cls.testing_mode = False

    @classmethod
    def fast_forward(cls, days=0, hours=0, seconds=0):
        cls.predictable_now += datetime.timedelta(days=days, hours=hours,
          seconds=seconds)
        cls.predictable_today = cls.predictable_now.date()

factory = DateFactory()
factory.reset()

setnow = factory.setnow
reset = factory.reset
fast_forward = factory.fast_forward
today = factory.today
now = factory.now
