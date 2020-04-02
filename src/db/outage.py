from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from .base import Base

from .device_or_circuit import *


class ScheduledOutage(Base):
    __tablename__ = 'scheduled_outages'

    id = Column(Integer, primary_key=True)
    provider = Column(String)
    outage_id = Column(String)
    dev_or_circ_id = Column(Integer, ForeignKey(DeviceOrCircuit.id, ondelete='SET NULL'))
    begin_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    data = Column(String) # with a new enough sqlalchemy we can use: Column(JSON)

    device_or_circuit = relationship('DeviceOrCircuit', foreign_keys='ScheduledOutage.dev_or_circ_id')


unique_provider_name = UniqueConstraint(ScheduledOutage.provider, ScheduledOutage.outage_id)
provider_id_idx = Index('scheduled_outages_provider_id_idx', ScheduledOutage.provider, ScheduledOutage.outage_id)


class DetectedOutage(Base):
    __tablename__ = 'detected_outages'

    id = Column(Integer, primary_key=True)
    dev_or_circ_id = Column(Integer, ForeignKey(DeviceOrCircuit.id, ondelete='SET NULL'))
    begin_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    data = Column(String) # with a new enough sqlalchemy we can use: Column(JSON)

    device_or_circuit = relationship('DeviceOrCircuit', foreign_keys='DetectedOutage.dev_or_circ_id')

    @property
    def provider(self):
        return self.device_or_circuit.provider


class UnscheduledOutage(Base):
    __tablename__ = 'unscheduled_outages'

    id = Column(Integer, primary_key=True)
    dev_or_circ_id = Column(Integer, ForeignKey(DeviceOrCircuit.id, ondelete='SET NULL'))
    begin_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    data = Column(String) # with a new enough sqlalchemy we can use: Column(JSON)

    device_or_circuit = relationship('DeviceOrCircuit', foreign_keys='UnscheduledOutage.dev_or_circ_id')

    @property
    def provider(self):
        return self.device_or_circuit.provider
