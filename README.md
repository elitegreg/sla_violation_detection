SLA Violation Detection
=======================

Requires:
---------

  * Python >= 3.7
  * SQLAlchemy
  * PostgreSQL (optional, can use sqlite3 in python as well)

---

Database Structure:
-------------------

  * **devices_or_circuits**: One entry for each device or circuit.
  * **device_circuits**: Describes a one-to-many relationship between a
    device and a circuit. E.g. a network switch might effect multiple
    circuits.
  * **last_processed**: Used to track the last time email/logs were
    loaded.
  * **scheduled_outages**: Scheduled maintenance outages from emails.
  * **detected_outages**: Detected outages from logs.
  * **unscheduled_outages**: Unscheduled outages derived from detected
    and scheduled outages.

Generated Database Schema:
--------------------------

```SQL
CREATE TABLE devices_or_circuits (
	id INTEGER NOT NULL, 
	provider VARCHAR, 
	service_id VARCHAR, 
	type VARCHAR(7) NOT NULL, 
	comment VARCHAR, 
	PRIMARY KEY (id), 
	CONSTRAINT type CHECK (type IN ('device', 'circuit')), 
	UNIQUE (provider, service_id)
);

CREATE INDEX devices_or_circuits_provider_id_idx ON devices_or_circuits (provider, service_id);

CREATE TABLE last_processed (
	name VARCHAR NOT NULL, 
	time DATETIME NOT NULL, 
	PRIMARY KEY (name)
);

CREATE TABLE device_circuits (
	devid INTEGER NOT NULL, 
	circid INTEGER NOT NULL, 
	PRIMARY KEY (devid, circid), 
	FOREIGN KEY(devid) REFERENCES devices_or_circuits (id) ON DELETE CASCADE, 
	FOREIGN KEY(circid) REFERENCES devices_or_circuits (id) ON DELETE CASCADE
);

CREATE TABLE scheduled_outages (
	id INTEGER NOT NULL, 
	provider VARCHAR, 
	outage_id VARCHAR, 
	dev_or_circ_id INTEGER, 
	begin_time DATETIME NOT NULL, 
	end_time DATETIME NOT NULL, 
	data VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(dev_or_circ_id) REFERENCES devices_or_circuits (id) ON DELETE SET NULL, 
	UNIQUE (provider, outage_id)
);

CREATE INDEX ix_scheduled_outages_begin_time ON scheduled_outages (begin_time);
CREATE INDEX scheduled_outages_provider_id_idx ON scheduled_outages (provider, outage_id);

CREATE TABLE detected_outages (
	id INTEGER NOT NULL, 
	dev_or_circ_id INTEGER, 
	begin_time DATETIME NOT NULL, 
	end_time DATETIME NOT NULL, 
	data VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(dev_or_circ_id) REFERENCES devices_or_circuits (id) ON DELETE SET NULL
);

CREATE INDEX ix_detected_outages_begin_time ON detected_outages (begin_time);

CREATE TABLE unscheduled_outages (
	id INTEGER NOT NULL, 
	dev_or_circ_id INTEGER, 
	begin_time DATETIME NOT NULL, 
	end_time DATETIME NOT NULL, 
	data VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(dev_or_circ_id) REFERENCES devices_or_circuits (id) ON DELETE SET NULL
);

CREATE INDEX ix_unscheduled_outages_begin_time ON unscheduled_outages (begin_time);
```

---

Basic Architechure:
-------------------

The code is well documented with docstrings. You should follow along by
looking at those.

  * Start in _main.py_, _poll()_ is the entry point into the application.
      * Uses _outage_loader.py_ to:
        * Uses _email_parser.py/helpdesk.py_ to load and parse emails
          into outage notifications.
        * Creates ORM objects for these scheduled outages and adds
          them to the database.
        * Uses _log_loader.py_ to load/parse log data to extract
          detected outages.
        * Creates ORM objects for these detected outages and adds
          them to the database.
        * Returns the newly created _DetectedOutages_.
      * Uses _unscheduled_outage_generator.py_ to:
        * Add _UnscheduledOutages_ to the db using the list of
          _DetectedOutages_ if they are not scheduled.
        * **NOTE:** Pay attention to the comments in
          _UnscheduledOutageGenerator.outage_is_scheduled(...)_.
          The code currently **does not** handle two cases:
          * If a detected outage overlaps a scheduled outage but any
            part of it falls outside the scheduled time, it is
            considered entirely unscheduled. This behavior may
            need to change based on requirements.
          * It's possible ProvderX schedules downtime for SwitchX.
            If we detect an outage with CircuitX which is on SwitchX,
            the application should realize that detected outage is
            scheduled. It can do this using the one-to-many mapping
            described in the device_circuits table.
        * Returns new _UnscheduledOutages_.
      * Uses _sla_handler.py_ to handle possible SLA violations.
        * SLAHandler uses plugins by provider to determine if an SLA
          has been violated.
        * There is no defined notification mechanism for SLA violations.
          The current behavior prints them to stdout. This could be
          added to a possible base class that also supports things like
          selecting data from _UnscheduledOutages_ that's necessary to
          verify the SLA.
      * **NOTE:** The email parser uses a plugin system based on the
        providers _from address_.

---

Demo
----

The script _demo.py_ is used to do a simple demo of the code. It loads some
data into the database and overrides the helpdesk/log apis to provide fake
data. The sample email is used as well.

  * **Outages**:
    * Email: fiberprovider, IC-99999, 20190409 06:00 - 10:00
    * Log: fiberprovider, IC-99999, 20190409 06:05 - 06:45
    * Log: fiberprovider, IC-99999, 20190409 11:05 - 11:25
  * **Output**:
```
SLA Violation!
  Provider: fiberprovider
  Service ID: IC-99999
  Begin Time: 2019-04-09T11:05:00
  End Time: 2019-04-09T11:25:00
```
