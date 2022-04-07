import connexion
from connexion import NoContent
import json
import os
from datetime import datetime
import datetime
import yaml
import logging.config
import requests
import uuid
from pykafka import KafkaClient
import time

MAX_EVENTS = 10
EVENT_FILE = "EVENT.json"

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

""" open configuration files """

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("reciever")
logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)

host_name = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
max_retry = app_config["events"]["retry"]
retry = 0
while retry < max_retry:
    logger.info(f"Try to connect Kafka Server, this is number {retry} try")
    try:
        client = KafkaClient(hosts=host_name)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        logger.info(f"Successfully connected to Kafka Server")
        break
    except:
        logger.error(f"Failed to connect to Kafka, this is number {retry} try")
        time.sleep(app_config["events"]["sleep"])
        retry += 1
        logger.info("retry in 10 second")


def report_coffeeFlavour_reading(body):

    trace_id = uuid.uuid4()
    body['trace_id'] = f'{trace_id}'
    body['date_create'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    msg = {"type": "event1",
           "datetime":
               datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer = topic.get_sync_producer()
    producer.produce(msg_str.encode('utf-8'))
    
    return NoContent, 201


def report_coffeeLocation_reading(body):
    trace_id = uuid.uuid4()
    body['trace_id'] = f'{trace_id}'
    body['date_create'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    msg = {"type": "event2",
           "datetime":
               datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer = topic.get_sync_producer()
    producer.produce(msg_str.encode('utf-8'))

    return NoContent, 201

def get_health():
    return 200

app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api("openapi.yaml", base_path="/receiver", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, debug=False)
