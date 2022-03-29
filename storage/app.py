import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from coffeeFlavour import CoffeeFlavour
from coffeeLocation import CoffeeLocation
import yaml
import logging
import logging.config
import uuid
import datetime
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import json

""" Read app_conf.yml """
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

user = app_config.get("datastore")["user"]
password = app_config.get("datastore")["password"]
hostname = app_config.get("datastore")["hostname"]
port = app_config.get("datastore")["port"]
db = app_config.get("datastore")["db"]

logger = logging.getLogger("storage")

"""Switching DB Section"""
DB_ENGINE = create_engine("sqlite:///readings.sqlite")

DB_ENGINE = create_engine(
    'mysql+pymysql://{}:{}@{}:{}/{}'.format(user, password, hostname, port, db))

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)



def report_coffeeLocation_reading(body):
    """ Receives a coffeeLocation reading """

    session = DB_SESSION()

    location = CoffeeLocation(body['location_id'],
                              body['location_name'],
                              body['timestamp'],
                              body['location_phone_number'],
                              body['location_Countrycode_number'],
                              body['trace_id'],
                              body['date_created']
                              )

    session.add(location)

    session.commit()
    session.close()

    trace_id = body['trace_id']
    event_name = "report_coffeeLocation_reading"
    logger.debug("Stored event {} request with a trace id of {}".format(
        event_name, trace_id))

    return NoContent, 201


def report_coffeeFlavour_reading(body):
    """ Receives a coffeeFlavour reading """

    session = DB_SESSION()

    flavour = CoffeeFlavour(body['coffee_id'],
                            body['coffee_name'],
                            body['timestamp'],
                            body['Flavour_points'],
                            body['Flavour_review_count'],
                            body['trace_id'],
                            body['date_created']
                            )

    session.add(flavour)

    session.commit()
    session.close()

    trace_id = uuid.uuid4()
    event_name = "report_coffeeFlavour_reading"
    logger.info("Stored event {} request with a trace id of {}".format(
        event_name, trace_id))

    return NoContent, 201


def get_coffeeLocation_readings(timestamp):
    """ Gets new coffee location readings after the timestamp """

    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(
        timestamp, "%Y-%m-%dT%H:%M:%SZ")
    readings = session.query(CoffeeLocation).filter(
        CoffeeLocation.date_created >= timestamp_datetime)
    results_list = []

    for reading in readings:
        results_list.append((reading.to_dict()))

    session.close()
    logger.info("Query for coffee location readings after %s returns %d results" % (
        timestamp, len(results_list)))

    logger.info(f"Connecting to DB. Hostname:{hostname}, Port:{port}")
    return results_list, 200


def get_coffeeFlavour_readings(timestamp):
    """ Gets new coffee flavour readings after the timestamp """

    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(
        timestamp, "%Y-%m-%dT%H:%M:%SZ")
    readings = session.query(CoffeeFlavour).filter(
        CoffeeFlavour.date_created >= timestamp_datetime)
    results_list = []

    for reading in readings:
        results_list.append((reading.to_dict()))
    print(results_list)
    session.close()
    logger.info("Query for coffee flavour readings after %s returns %d results" % (
        timestamp, len(results_list)))

    logger.info(f"Connecting to DB. Hostname:{hostname}, Port:{port}")
    return results_list, 200


def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)

        logger.info("Message: %s" % msg)

        payload = msg["payload"]
        if msg["type"] == 'event1':
            session = DB_SESSION()

            flavour = CoffeeFlavour(payload['coffee_id'],
                                    payload['coffee_name'],
                                    payload['timestamp'],
                                    payload['Flavour_points'],
                                    payload['Flavour_review_count'],
                                    payload['trace_id'],
                                    payload['date_create']
                                    )

            session.add(flavour)

            session.commit()
            session.close()

        elif msg["type"] == 'event2':
            session = DB_SESSION()

            location = CoffeeLocation(payload['location_id'],
                                      payload['location_name'],
                                      payload['timestamp'],
                                      payload['location_phone_number'],
                                      payload['location_Countrycode_number'],
                                      payload['trace_id'],
                                      payload['date_create']
                                      )

            session.add(location)

            session.commit()
            session.close()

        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__== "__main__":
    t1 = Thread(target=process_messages)
    logger.info(f"t1 = {t1}")
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090, debug=True)