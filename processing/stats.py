from sqlalchemy import Column, Integer, String, DateTime
from base import Base


class Stats(Base):
    """Processing Statistics"""

    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_location_phone_readings = Column(Integer, nullable=False)
    max_flavour_points_reading = Column(Integer, nullable=False)
    num_flavour_review_count_readings = Column(Integer, nullable=False)
    num_location_Countrycode_number_readings = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_location_phone_readings, max_flavour_points_reading, num_flavour_review_count_readings, num_location_Countrycode_number_readings, last_updated):
        """ Initializes a processing statistics objet """
        self.num_location_phone_readings = num_location_phone_readings
        self.max_flavour_points_reading = max_flavour_points_reading
        self.num_flavour_review_count_readings = num_flavour_review_count_readings
        self.num_location_Countrycode_number_readings = num_location_Countrycode_number_readings
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_location_phone_readings'] = self.num_location_phone_readings
        dict['max_flavour_points_reading'] = self.max_flavour_points_reading
        dict['num_flavour_review_count_readings'] = self.num_flavour_review_count_readings
        dict['num_location_Countrycode_number_readings'] = self.num_location_Countrycode_number_readings
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")

        return dict


