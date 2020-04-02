from dataclasses import dataclass
from datetime import datetime


"""Encapsulates a detected outage from the log files.

Attributes:
    provider (str): Identifies a provider. Must match what's in the
                    DeviceCircuits db table.
    service_id (str): Indentifies a device or circuit. Must match what's
                      int the DeviceCircuits db table.
    begin (datetime): Time of the scheduled outage start.
    end (datetime): Time of the scheduled outage end.
    data (dict): Extra data that will be stored in JSON in the database
"""
@dataclass(frozen=True)
class Outage:
    provider: str
    service_id: str
    begin: datetime
    end: datetime
    data: dict


'''Load outages from logs.

This method must use the log access api to get log data and extract
necessary information to construct Outage objects and yield them.

Args:
    last_processed_time (datetime)

Yields:
    Outage
'''
def load_outages_from_logs(last_processed_time):
    # just force this to be a generator
    if False:
        yield None
