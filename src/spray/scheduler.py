from datetime import timedelta
import datetime
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


class PeriodicEvent(object):

    def __init__(self, id, gov_class, gov_id, gov_field,
      expiry_date=None, mm=None, accessor=None, external_nix=None):
        self.id = id
        self.gov_class = gov_class
        self.gov_id = gov_id
        self.gov_field = gov_field
        self.expiry_date = expiry_date
        self.mm = mm
        self.accessor = accessor
        self.external_nix = external_nix
        self.schedule_next()

    def __repr__(self):
        return 'PeriodicEvent id:%r gov_class:%r gov_id:%r gov_field:%r' % (
          self.id, self.gov_class, self.gov_id, self.gov_field)

    def schedule_next(self):
        "sets the next_occurrence or None if expired"
        # see if the external method wants to stop the event
        if self.external_nix and self.external_nix(self):
            self.next_occurrence = None
            return None
        # see if a pre-ordained expiry has elapsed
        nn = datetime.datetime.now()
        if self.expiry_date and nn > self.expiry_date:
            self.next_occurrence = None
            return None
        # compute the next time, or None
        pp = self.period()
        tp = self._get_timepoint()
        if pp.total_seconds() < 0:
            # negative means counting to end
            pp = abs(pp)
            dm = divmod((tp - nn).total_seconds(), pp.total_seconds())
            self.next_occurrence = dm[0] and (nn + pp) or None
        else:
            # pos is counting from a start time
            dm = divmod((nn - tp).total_seconds(), pp.total_seconds())
            self.next_occurrence = nn + datetime.timedelta(seconds=dm[1])
        return self.next_occurrence

    def _get_timepoint(self):
        "returns value provided by the plugable accessor"
        acc = self.accessor
        return acc(self.gov_class, self.gov_id, self.gov_field)

    def period(self):
        "ask the mm for the period for this event type - negative if countdown"
        rr = self.mm.get_rows_for_event(self.id)
        p = rr[0]['period']
        for r in rr[1:]:
            assert p == r['period']
        if not p:
            return None
        return _to_interval(p)

    def is_expired(self):
        self.schedule_next()
        return self.next_occurrence is not None
