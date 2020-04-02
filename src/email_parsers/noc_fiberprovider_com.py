from datetime import datetime
from email_parser import *

import re

_parser_re = re.compile(r'^Subject: (?P<subj>.*?)$'
                       r'(.*?)'
                       r'^PW Reference Number: (?P<id>\w+)$'
                       r'(.*?)'
                       r'^Start Date and Time: (?P<begin>\d{4}-\w{3}-\d{2} \d{2}:\d{2}\s+\w+)$'
                       r'(.*?)'
                       r'^End Date and Time: (?P<end>\d{4}-\w{3}-\d{2} \d{2}:\d{2}\s+\w+)$'
                       r'(.*?)'
                       r'^Action and Reason: (?P<action_reason>.*?(New try for cancelled (?P<cancelled>\w+)\.)*)$'
                       r'(.*?)'
                       r'^Location of work: (?P<location>.*?)$'
                       r'(.*?)'
                       r'^Service ID: (?P<service_id>.*?)$'
                       r'(.*?)'
                       r'^Impact: (?P<impact>.*?)$'
                       r'(.*?)'
                       r'^E-mail: (?P<email>.*?)$'
                       r'(.*?)'
                       r'^Phone: (?P<phone>.*?)$'
                       , re.MULTILINE|re.IGNORECASE|re.DOTALL)


@register_parser('noc@fiberprovider.com')
def parse(fromaddr, content):
    mo = _parser_re.match(content)
    if not mo:
        raise EmailParseError('Failed to parse email')

    try:
        begin = datetime.strptime(mo.group('begin'), '%Y-%b-%d %H:%M %Z')
        end = datetime.strptime(mo.group('end'), '%Y-%b-%d %H:%M %Z')
    except ValueError:
        raise EmailParseError('Failed to parse begin/end times')

    return MaintenanceNotification(
        'fiberprovider',
        mo.group('id'),
        mo.group('cancelled'),
        mo.group('service_id'),
        begin,
        end,
        mo.group('subj'),
        mo.group('action_reason'),
        mo.group('location'),
        mo.group('impact'),
        mo.group('email'),
        mo.group('phone'))
