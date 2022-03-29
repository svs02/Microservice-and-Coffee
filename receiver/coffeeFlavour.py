from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class CoffeeFlavour(Base):
    """ Flavour """

    __tablename__ = "coffeeFlavour"

    id = Column(Integer, primary_key=True)
    coffee_id = Column(String(250), nullable=False)
    coffee_name = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    Flavour_points = Column(Integer, nullable=False)
    Flavour_review_count = Column(Integer, nullable=False)
    trace_id = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, coffee_id, coffee_name, timestamp, Flavour_points, Flavour_review_count, trace_id, date_created):
        """ Initializes a heart rate reading """
        self.coffee_id = coffee_id
        self.coffee_name = coffee_name
        self.timestamp = timestamp
        self.Flavour_points = Flavour_points
        self.Flavour_review_count = Flavour_review_count
        self.trace_id = trace_id
        self.date_created = date_created


    def to_dict(self):
        """ Dictionary Representation of a heart rate reading """
        dict = {}
        dict['id'] = self.id
        dict['coffee_id'] = self.coffee_id
        dict['coffee_name'] = self.coffee_name
        dict['Flavour_points'] = self.Flavour_points
        dict['Flavour_review_count'] = self.Flavour_review_count
        dict['timestamp'] = self.timestamp
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
