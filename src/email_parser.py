from dataclasses import dataclass
from datetime import datetime

"""Class to represent the scheduled maintenance loaded from email.

Attributes:

    provider (str): Identifies a provider. Must match what's in the
                    DeviceCircuits db table.
    update_id (str): Provider provided identifier for the notification.
                     If not None, causes a new scheduled outage to be
                     added.
    update_id (str): Provider provided identifier for the notification.
                     If not None, removes this scheduled outage.
    service_id (str): Indentifies a device or circuit. Must match what's
                      int the DeviceCircuits db table.
    begin (datetime): Time of the scheduled outage start.
    end (datetime): Time of the scheduled outage end.
    subject (str): Email subject.
    action_and_reason (str): The action/reason for the maintenance.
    location (str): Location of device/circuit.
    impact (str)
    email (str)
    phone (str)
"""
@dataclass(frozen=True)
class MaintenanceNotification:
    provider: str
    update_id: str
    cancel_id: str
    service_id: str
    begin: datetime
    end: datetime
    subject: str
    action_and_reason: str
    location: str
    impact: str
    email: str
    phone: str

"""Class to parse the maintenance emails.

Parses maintenance emails using a plugin system where each from email address 
is a plugin.
"""
class EmailParser:
    _per_provider_parsers = {}

    """Register a plugin.

    Args:
        provider (str): email address of the provider
        parser (func(str, str)): parse function.
    """
    @staticmethod
    def register_parser(provider, parser):
        EmailParser._per_provider_parsers[provider] = parser

    """Parse a maintenance email.
    
    Args:
        fromaddr (str): provider email address
        content (str): email content

    Returns:
        MaintenanceNotification

    Raises:
        EmailParseError: Unable to parse email.
    """
    @staticmethod
    def parse(fromaddr, content):
        parser = EmailParser._per_provider_parsers.get(fromaddr)

        if not parser:
            raise EmailParseError(f'No parser for {fromaddr}')

        return parser(fromaddr, content)


"""Decorator to register a parser with EmailParser.

Args:
    provider (str): provider's email address
"""
class register_parser:
    def __init__(self, provider):
        self._provider = provider

    def __call__(self, func):
        EmailParser.register_parser(self._provider, func)
        return func


class EmailParseError(RuntimeError):
    pass


# load plugins
import email_parsers
