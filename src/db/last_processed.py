from sqlalchemy import Column, DateTime, String

from .base import Base


class LastProcessed(Base):
    __tablename__ = 'last_processed'

    name = Column(String, primary_key=True)
    time = Column(DateTime, nullable=False)
