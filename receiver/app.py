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


def writting_json(body):

    new_object = {
        "received timestamp": str(datetime.now()),
        "request_data": body
    }

    if os.path.isfile(EVENT_FILE):
        with open(EVENT_FILE, "r+") as file:
            content = json.load(file)
    else:
        content = []

    if "location_id" in body:
        new_object = f"location_id: {body['location_id']}, location_name: {body['location_name']}, location_phone_number: {body['location_phone_number']}, location_Countrycode_number: {body['location_Countrycode_number']}"
    if "coffee_id" in body:
        new_object = f"coffee_id: {body['coffee_id']}, coffee_name:{body['coffee_name']}, Flavour_points: {body['Flavour_points']}, Flavour_review_count: {body['Flavour_review_count']}"

    content.append(new_object)

    if len(content) > MAX_EVENTS:
        content = content[1:]

    object = json.dumps(content, indent=4)

    with open(EVENT_FILE, "w+") as outfile:
        outfile.write(object)
    return object


def report_coffeeFlavour_reading(body):

    trace_id = uuid.uuid4()
    body['trace_id'] = f'{trace_id}'
    body['date_create'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = json.dumps(body)
    url = app_config["eventstore1"]["url"]
    # r = requests.post(url, data=payload, headers={
    #                   "Content-Type": "application/json"})

    client = KafkaClient(
        hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = {"type": "event1",
           "datetime":
               datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    # event_name = "report_coffeeFlavour_reading"
    # status_code = requests.post(url, json.dumps(body), headers={
    #                             "Content-Type": "application/json"})
    # logger.info("Received event {} request with a trace id of {}".format(
    #     event_name, trace_id))
    # logger.info("Returned event {} response {} with status {}".format(
    #     event_name, trace_id, status_code))

    return NoContent, 201


def report_coffeeLocation_reading(body):
    trace_id = uuid.uuid4()
    body['trace_id'] = f'{trace_id}'
    body['date_create'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = json.dumps(body)
    url = app_config["eventstore2"]["url"]
    # r = requests.post(url, data=payload, headers={
    #                   "Content-Type": "application/json"})

    # event_name = "report_coffeeLocation_reading"
    # status_code = requests.post(url, json.dumps(body), headers={
    #                             "Content-Type": "application/json"})
    # logger.info("Received event {} request with a trace id of {}".format(
    #     event_name, trace_id))
    # logger.info("Returned event {} response {} with status {}".format(
    #     event_name, trace_id, status_code))

    client = KafkaClient(
        hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()
    msg = {"type": "event2",
           "datetime":
               datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, debug=False)
