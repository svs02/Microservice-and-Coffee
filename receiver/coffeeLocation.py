from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class CoffeeLocation(Base):
    """ Location """

    __tablename__ = "coffeeLocation"

    id = Column(Integer, primary_key=True)
    location_id = Column(String(250), nullable=False)
    location_name = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    location_phone_number = Column(Integer, nullable=False)
    location_Countrycode_number = Column(Integer, nullable=False)
    trace_id = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, location_id, location_name, timestamp, location_phone_number, location_Countrycode_number, trace_id, date_created):
        """ Initializes a coffeeLocation reading """
        self.location_id = location_id
        self.location_name = location_name
        self.timestamp = timestamp
        self.location_phone_number = location_phone_number
        self.location_Countrycode_number = location_Countrycode_number
        self.trace_id = trace_id
        self.date_created = date_created

    def to_dict(self):
        """ Dictionary Representation of a coffeeLocation reading """
        dict = {}
        dict['id'] = self.id
        dict['location_id'] = self.location_id
        dict['location_name'] = self.location_name
        dict['location_phone_number'] = self.location_phone_number
        dict['location_Countrycode_number'] = self.location_Countrycode_number
        dict['timestamp'] = self.timestamp
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
