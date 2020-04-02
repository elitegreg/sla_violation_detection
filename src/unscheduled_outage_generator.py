from db import db_session
from db.device_or_circuit import Type as DoCType
from db.outage import *

"""Populates the UnscheduledOutage table.

Uses the detected outages as well as scheduled outages to generate
the UnscheduledOutage table.
"""
class UnscheduledOutageGenerator:
    """Add unscheduled outages as needed.

    Args:
        list[DetectedOutage]

    Returns:
        list[UnscheduledOutage]: newly created UnscheduledOutages
    """
    def add_if_needed(self, detected_outages):
        result = []
        for outage in detected_outages:
            if not self.outage_is_scheduled(outage):
                result.append(self.create_unscheduled_outage(outage))
        return result

    """Check if a detected outage is scheduled.

    The implementation is incomplete: see comments in code below.

    Args:
        outage (DetectedOutage)

    Returns:
        bool: True if outage is scheduled
    """
    def outage_is_scheduled(self, outage):
        # TODO: this needs to somehow consider the case of a scheduled outage
        # from 1:00 - 2:00 with an outage from 1:00 - 2:10. Presumably, the
        # extra 10 minutes would count against the SLA?!?! For now, if any
        # of the outage is outside the scheduled time, the whole outage is
        # considered unscheduled.
        sched_outage = db_session.query(ScheduledOutage).filter(
            ScheduledOutage.provider == outage.provider).filter(
            ScheduledOutage.dev_or_circ_id == outage.dev_or_circ_id).filter(
            ScheduledOutage.begin_time <= outage.begin_time).filter(
            ScheduledOutage.end_time >= outage.end_time).first()

        if sched_outage:
            return True

        # TODO: It's possible we detected an outage with a circuit that is
        # caused by a scheduled outage of a device or vice versa. We can use
        # the DeviceCircuits table to map these (one device to many circuits)

        return False

    """Creates a new UnscheduledOutage and adds it to the db.

    Args:
        outage (DetectedOutage)

    Returns:
        UnscheduledOutage
    """
    def create_unscheduled_outage(self, outage):
        outage = UnscheduledOutage(dev_or_circ_id=outage.dev_or_circ_id,
            begin_time=outage.begin_time, end_time=outage.end_time,
            data=outage.data)
        db_session.add(outage)
        db_session.commit()
        return outage
