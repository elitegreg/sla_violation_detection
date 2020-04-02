from sqlalchemy import Column, Index, Integer, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base

import enum


class Type(enum.Enum):
    device = 1
    circuit = 2


class DeviceOrCircuit(Base):
    __tablename__ = 'devices_or_circuits'

    id = Column(Integer, primary_key=True)
    provider = Column(String)
    service_id = Column(String)
    type = Column(Enum(Type), nullable=False)
    comment = Column(String)
    # Possibly add other useful information, such as points of contact


unique_provider_id = UniqueConstraint(DeviceOrCircuit.provider, DeviceOrCircuit.service_id)
provider_id_idx = Index('devices_or_circuits_provider_id_idx', DeviceOrCircuit.provider, DeviceOrCircuit.service_id)


class DeviceCircuits(Base):
    __tablename__ = 'device_circuits'

    devid = Column(Integer, ForeignKey(DeviceOrCircuit.id, ondelete='CASCADE'), primary_key=True)
    circid = Column(Integer, ForeignKey(DeviceOrCircuit.id, ondelete='CASCADE'), primary_key=True)

    device = relationship('DeviceOrCircuit', foreign_keys='DeviceCircuits.devid')
    circuit = relationship('DeviceOrCircuit', foreign_keys='DeviceCircuits.circid')
