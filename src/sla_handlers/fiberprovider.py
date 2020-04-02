from sla_handler import register_handler

@register_handler('fiberprovider')
def handle_unscheduled_outage(outage):
    # For this provider, there is a 0% tolerance for unscheduled outages!
    # For others, we could query UnscheduledOutages over time to see what
    # other outages there have been, and handle things as needed! Any form
    # of alert we want to use can be used here: logging, email, network
    # message, whatever. For example, we will just use print(...)
    print('SLA Violation!\n'
          f'\tProvider: {outage.provider}\n'
          f'\tService ID: {outage.device_or_circuit.service_id}\n'
          f'\tBegin Time: {outage.begin_time.isoformat()}\n'
          f'\tEnd Time: {outage.end_time.isoformat()}\n')

