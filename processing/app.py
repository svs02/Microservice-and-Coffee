import os

import connexion
import swagger_ui_bundle
import requests
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
from base import Base
from stats import Stats
import yaml
import logging.config
import uuid
import datetime
import random
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

DB_ENGINE = create_engine("sqlite:///stats.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

mysql_db_url = app_config['eventstore']['url']
logger = logging.getLogger("service")


def populate_stats():
    session = DB_SESSION()
    logger.info("Starting pop_stats")
    results = session.query(Stats).order_by(Stats.id.desc()).first()
    current_date = datetime.datetime.now()
    if not results:
        results = {
            "id": 0,
            "num_location_phone_readings": 0,
            "max_flavour_points_reading": 0,
            "num_flavour_review_count_readings": 0,
            "num_location_Countrycode_number_readings": 0,
            "last_updated": current_date
        }

    if not isinstance(results, dict):
        results = results.to_dict()

    new_results = {
        "id": 0,
        "num_location_phone_readings": 0,
        "max_flavour_points_reading": 0,
        "num_flavour_review_count_readings": 0,
        "num_location_Countrycode_number_readings": 0,
        "last_updated": current_date
    }

    start_timestamp = results['last_updated']
    logger.debug(start_timestamp)
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    logger.debug(current_timestamp)

    # location part

    location_response = requests.get(app_config["eventstore"]["url"] +
                                    "/coffee/location?start_timestamp=" +
                                    f"{start_timestamp}" + "&end_timestamp=" +
                                    f"{current_timestamp}")

    if location_response.status_code != 200:
        logger.error("get_location is invalid request")
    else:
        location_response_data = location_response.json()
        logger.info(
            f"Total number of new location is: {len(location_response_data)}")

        new_results['num_location_phone_readings'] = results['num_location_phone_readings'] + \
            len(location_response_data)
        new_results['num_location_Countrycode_number_readings'] = results['num_location_Countrycode_number_readings'] + \
            len(location_response_data)

        li = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        max_phone_readings = new_results['num_location_phone_readings']
        max_Countrycode_number_readings = new_results['num_location_Countrycode_number_readings']
        for i in location_response_data:
            try:
                max_phone_readings = max(
                    max_phone_readings, i['num_location_phone_readings'])
            except KeyError:
                print(f"\n\n{i}\n\n")
            try:
                max_Countrycode_number_readings = max(
                    max_Countrycode_number_readings, i['num_location_Countrycode_number_readings'])
            except KeyError:
                print(f"\n\n{i}\n\n")
            logger.debug(f"locaion event {i['trace_id']} processed")

        max_phone_readings = max_phone_readings + random.choice(li)
        max_Countrycode_number_readings = max_Countrycode_number_readings + \
            random.choice(li)

        new_results['num_location_phone_readings'] = max_phone_readings
        new_results['num_location_Countrycode_number_readings'] = max_Countrycode_number_readings

    # flavour part

    flavour_response = requests.get(app_config["eventstore"]["url"] +
                                    "/coffee/flavour?start_timestamp=" +
                                    f"{start_timestamp}" + "&end_timestamp=" +
                                    f"{current_timestamp}")

    if flavour_response.status_code != 200:
        logger.error("get_flavour is invalid request")
    else:
        flavour_response_data = flavour_response.json()
        logger.info(
            f"Total number of new flavour is: {len(flavour_response_data)}")

        new_results['max_flavour_points_reading'] = results['max_flavour_points_reading'] + len(
            flavour_response_data)
        new_results['num_flavour_review_count_readings'] = results['num_flavour_review_count_readings'] + len(
            flavour_response_data)

        li = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        max_flavour_points_reading = new_results['max_flavour_points_reading']
        num_flavour_review_count_readings = new_results['num_flavour_review_count_readings']
        for i in flavour_response_data:
            try:
                max_flavour_points_reading = max(
                    max_flavour_points_reading, i['max_flavour_points_reading'])
            except KeyError:
                print(f"\n\n{i}\n\n")
            try:
                num_flavour_review_count_readings = max(num_flavour_review_count_readings,
                                                        i['num_flavour_review_count_readings'])
            except KeyError:
                print(f"\n\n{i}\n\n")
            logger.debug(f"flavour event {i['trace_id']} processed")

        max_flavour_points_reading = max_flavour_points_reading + \
            random.choice(li)
        num_flavour_review_count_readings = num_flavour_review_count_readings + \
            random.choice(li)
        if max_flavour_points_reading > 500:
            max_flavour_points_reading = 500

        new_results['max_flavour_points_reading'] = max_flavour_points_reading
        new_results['num_flavour_review_count_readings'] = num_flavour_review_count_readings

    add_stats = Stats(new_results["num_location_phone_readings"], new_results["max_flavour_points_reading"],
                      new_results["num_flavour_review_count_readings"], new_results["num_location_Countrycode_number_readings"], new_results["last_updated"])

    session.add(add_stats)
    session.commit()
    session.close()

    logger.debug(f"Processing data has been done. {new_results}")
    logger.info(f"Periodic Processing Ends")


def get_stats():
    """ Get stats event """
    logger.info("get_stats request has started")
    session = DB_SESSION()
    last_updated = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    if last_updated == None:
        logger.error("Statistics do not exist!")
    data_dict = last_updated.to_dict()
    logger.debug(f"Coverted to dictionary: {data_dict}")
    logger.info("get_stats requests has completed!")
    session.close()
    return data_dict, 200


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='./')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    # run our standalone event server
    init_scheduler()
    app.run(port=8100, use_reloader=False)
