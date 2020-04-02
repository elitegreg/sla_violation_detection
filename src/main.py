from outage_loader import *
from sla_handler import *
from unscheduled_outage_generator import *

import argparse
import time
import pprint


"""Polls for new outages and checks SLAs.

Uses OutageLoader, UnscheduledOutageGenerator and SLAHandler to load
scheduled and detected outages, find unscheduled outages, and report
those to the SLAHandler. The SLAHandler can then determine if an SLA
has been violated.

Args:
    poll_interval (int): seconds between polls. 0 == No poll
"""
def poll(poll_interval):
    loader = OutageLoader()
    gen = UnscheduledOutageGenerator()
    sla_handler = SLAHandler()

    while True:
        loader.load_new_scheduled_outages()
        detected_outages = loader.load_new_detected_outages()
        if detected_outages:
            unscheduled_outages = gen.add_if_needed(detected_outages)
            for outage in unscheduled_outages:
                sla_handler.handle_unscheduled_outage(outage)

        if poll_interval > 0:
            time.sleep(poll_interval)
        else:
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--poll-interval', type=int, default=299,
                        help='Poll interval in seconds')

    args = parser.parse_args()

    poll(args.poll_interval)
