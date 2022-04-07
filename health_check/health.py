from tokenize import String
from sqlalchemy import Column, Integer, DateTime, String
from base import Base


class Health(Base):
    """ Processing Statistics """
    __tablename__ = "health"
    id = Column(Integer, primary_key=True)
    receiver = Column(String(250), nullable=False)
    storage = Column(String(250), nullable=False)
    processing = Column(String(250), nullable=False)
    audit_log = Column(String(250), nullable=True)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, receiver, storage,
                 processing, audit_log,
                 last_updated):
        """ Initializes a processing statistics objet """
        self.receiver = receiver
        self.storage = storage
        self.processing = processing
        self.audit_log = audit_log
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['receiver'] = self.receiver
        dict['storage'] = self.storage
        dict['processing'] = self.processing
        dict['audit_log'] = self.audit_log
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
        return dict
