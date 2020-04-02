from db import db_session
from db.device_or_circuit import DeviceOrCircuit, Type as DoCType
from db.last_processed import LastProcessed
from db.outage import DetectedOutage, ScheduledOutage

from email_parser import EmailParser

import helpdesk
import log_loader

from datetime import datetime

import json


'''The purpose of this class is to load NEW outages, both scheduled (from
email) and detected (from log files).

Design choices:
    * The outages are loaded on demand, intended to be polled periodically.
      An alternative approach would be to trigger when new data is
      available. This would be an easy change to make if needed.
    * We use a stored timestamp for both email/log files that keeps track
      of the last time we loaded data from those apis.
'''
class OutageLoader:
    epoch = datetime(1970, 1, 1)

    def __init__(self):
        # Initialize objects to track the last time we polled email/logs
        self._last_processed_email = self.get_last_processed('email')
        self._last_processed_log = self.get_last_processed('log')

        if self._last_processed_email is None:
            self._last_processed_email = LastProcessed(name='email', time=self.epoch)
            db_session.add(self._last_processed_email)
            db_session.commit()
        if self._last_processed_log is None:
            self._last_processed_log = LastProcessed(name='log', time=self.epoch)
            db_session.add(self._last_processed_log)
            db_session.commit()

    """Get the LastProcessed object for the given name.
    
    Args:
        name (str): `email` or `log`

    Returns:
        LastProcessed: Has a `time` member
    """
    def get_last_processed(self, name):
        return db_session.query(
            LastProcessed).filter_by(name=name).one_or_none()

    """Load new scheduled outages.

    Use helpdesk api to fetch new emails then parse emails to find outages.
    Call self.create_scheduled_outage(...) with outage data loaded.

    Returns:
        bool: True if new outages loaded, False for no new outages
    """
    def load_new_scheduled_outages(self):
        for (time, fromaddr, content) in \
                helpdesk.load_new_emails(self._last_processed_email.time):
            notification = EmailParser.parse(fromaddr, content)
            if notification.cancel_id:
                # Need to cancel an old scheduled outage
                db_session.query(ScheduledOutage).filter_by(
                    provider=notification.provider,
                    outage_id=notification.cancel_id).delete()
            if notification.update_id:
                # Need to create a scheduled outage
                self.create_scheduled_outage(notification)
            self._last_processed_email.time = time
            db_session.commit()
        else:
            return False
        return True

    """Load new detected outages.

    Use log data api to fetch new logs then parse logs to find outages.
    Call self.create_detected_outage(...) with outage data loaded.

    Returns:
        list[DetectedOutage]: New detected outages loaded
    """
    def load_new_detected_outages(self):
        result = []
        for (time, outage) in log_loader.load_outages_from_logs(
                self._last_processed_log.time):
            result.append(self.create_detected_outage(outage.provider, 
                outage.service_id, outage.begin, outage.end, outage.data))
            self._last_processed_log_time = time
            db_session.commit()
        return result

    """Lookup device/circuit id.

    Args:
        provider (str)
        service_id (str)

    Returns:
        int: device/circuit id or None if not found
    """
    def get_device_or_circuit_id(self, provider, service_id):
        row = db_session.query(DeviceOrCircuit.id).filter_by(
            provider=provider, service_id=service_id).one_or_none()
        return row.id if row else None

    """Create detected outage object and add it to the database.

    Args:
        provider (str)
        service_id (str)
        begin (datetime): Beginning time of outage
        end (datetime): Ending time of outage
        data (dict): Extra data that will be stored in JSON in the database

    Returns:
        DetectedOutage

    Raises:
        OutageLoaderError: Cannot find device/circuit
    """
    def create_detected_outage(self, provider, service_id, begin, end, data={}):
        dev_or_circ_id = self.get_device_or_circuit_id(provider, service_id)
        if not dev_or_circ_id:
            raise OutageLoaderError(
                f'Failed to find device/circuit for {provider}:{service_id}')
        outage = DetectedOutage(dev_or_circ_id=dev_or_circ_id,
            begin_time=begin, end_time=end, data=json.dumps(data))
        db_session.add(outage)
        return outage
        
    """Create scheduled outage object and add it to the database.

    Args:
        notification (email_parser.MaintenanceNotification)

    Returns:
        DetectedOutage

    Raises:
        OutageLoaderError: Cannot find device/circuit
    """
    def create_scheduled_outage(self, notification):
        dev_or_circ_id = self.get_device_or_circuit_id(
            notification.provider, notification.service_id)
        if not dev_or_circ_id:
            raise OutageLoaderError(
                f'Failed to find device/circuit for {notification.provider}:{notification.service_id}')
        outage = ScheduledOutage(provider=notification.provider,
            outage_id=notification.update_id,  dev_or_circ_id=dev_or_circ_id,
            begin_time=notification.begin, end_time=notification.end,
            data=json.dumps({
                'Subject' : notification.subject,
                'ActionReason' : notification.action_and_reason,
                'Location' : notification.location,
                'Impact' : notification.impact,
                'Email' : notification.email,
                'Phone' : notification.phone,
            }))
        db_session.add(outage)
        return outage
        

class OutageLoaderError(RuntimeError):
    pass
