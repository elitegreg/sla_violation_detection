from .base import *
from .device_or_circuit import *
from .last_processed import *
from .outage import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os


engine = create_engine('sqlite:///:memory:', echo=os.getenv('SQLALCHEMY_ECHO') is not None)
db_session = sessionmaker(bind=engine)()

Base.metadata.create_all(engine)

