from db import db_session
from db.device_or_circuit import DeviceOrCircuit, Type as DoCType
from main import poll
from outage_loader import *

import helpdesk
import log_loader

from datetime import datetime


with open('../data/provider_email.txt') as f:
    content = f.read()
emails = [('noc@fiberprovider.com', content)]

outages = [
    log_loader.Outage(
        'fiberprovider', 'IC-99999', datetime(2019, 4, 9, 6, 5),
        datetime(2019, 4, 9, 6, 45), {}),
    log_loader.Outage(
        'fiberprovider', 'IC-99999', datetime(2019, 4, 9, 11, 5),
        datetime(2019, 4, 9, 11, 25), {}),
]


# Mock up some stuff for a demo

def load_new_emails(last_processed_time):
    while len(emails):
        (fromaddr, content) =  emails.pop(0)
        yield (last_processed_time, fromaddr, content)


helpdesk.load_new_emails = load_new_emails


def load_outages_from_logs(last_processed_time):
    while len(outages):
        yield (last_processed_time, outages.pop(0))


log_loader.load_outages_from_logs = load_outages_from_logs


db_session.add(DeviceOrCircuit(
    provider='fiberprovider', service_id='IC-99999', type=DoCType.circuit))


if __name__ == '__main__':
    poll(0)
