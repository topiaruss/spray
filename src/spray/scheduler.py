from datetime import timedelta
from spray.utils import ourtime
import spray
import string

UNITS = dict(d='days', w='weeks', m='months', y='years')


def _to_interval(stringint):
    "turns strings like -1w or 2d into periods"
    unit = ''.join([c for c in stringint.lower() if c in string.letters])
    unit = UNITS[unit]
    qty = ''.join([c for c in stringint if c in string.digits])
    sign = '-' in stringint and -1 or 1
    qty = int(qty) * sign
    arg = {unit: qty}
    return timedelta(**arg)


class PeriodicEventQ(object):

    def __init__(self):
        pass


class PeriodicEvent(object):

    def __init__(self, *args, **kwargs):
        # flexible args in case used as mixed-in
#       if isinstance(self, isinstance(self, spray.scheduler.PeriodicEvent)):
        if self.__class__ == spray.scheduler.PeriodicEvent:
            # only if we are a standalone, not mixin
            self.eid = kwargs.get('eid')
            self.gov_class = kwargs.get('gov_class')
            self.gov_id = kwargs.get('gov_id')
            self.gov_field = kwargs.get('gov_field')
            self.expiry_date = kwargs.get('expiry_date')
            assert all((self.eid, self.gov_class, self.gov_id, self.gov_field))
            # we don't automatically schedule_next in a django mix-in
            mm = kwargs.get('mm')
            accessor = kwargs.get('accessor')
            external_nix = kwargs.get('external_nix')
            self.schedule_next(mm, accessor, external_nix)

    def __repr__(self):
        return 'PeriodicEvent id:%r gov_class:%r gov_id:%r gov_field:%r' % (
          self.eid, self.gov_class, self.gov_id, self.gov_field)

    def schedule_next(self, mm, accessor, external_nix=None):
        "sets the next_occurrence or None if expired"
        # see if the external method wants to stop the event
        if external_nix and external_nix(self):
            self.next_occurrence = None
            return None
        # see if a pre-ordained expiry has elapsed
        nn = ourtime.now()
        if self.expiry_date and nn >= self.expiry_date:
            self.next_occurrence = None
            return None
        # compute the next time, or None
        pp = self.period(mm)
        tp = self._get_timepoint(accessor)
        if pp.total_seconds() < 0:
            # negative means counting to end
            pp = abs(pp)
            dm = divmod((tp - nn).total_seconds(), pp.total_seconds())
            self.next_occurrence = dm[0] and (tp - (pp * int(dm[0]))) or None
        else:
            # pos is counting from a start time
            dm = divmod((nn - tp).total_seconds(), pp.total_seconds())
            periods_elapsed = int(dm[0])
            self.next_occurrence = tp + ((periods_elapsed + 1) * pp)
        return self.next_occurrence

    def _get_timepoint(self, accessor):
        "returns value provided by the plugable accessor"
        return accessor(self.gov_class, self.gov_id, self.gov_field)

    def period(self, mm):
        "ask the mm for the period for this event type - negative if countdown"
        rr = mm.get_rows_for_event(self.eid)
        p = rr[0]['period']
        for r in rr[1:]:
            assert p == r['period']
        if not p:
            return None
        return _to_interval(p)

    def is_expired(self, external_nix=None):
        "updates next_occurence and checks if it's expired"
        return (self.next_occurrence is None) or\
          (external_nix and external_nix(self))
