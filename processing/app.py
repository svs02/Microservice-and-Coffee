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
    """ Periodically update stats """
    logger.info(f"Populate stats has started")
    current_date = datetime.datetime.now()
    session = DB_SESSION()
    if os.path.isfile('stats.sqlite'):
        last_updated = session.query(Stats).order_by(Stats.last_updated.desc()).first()
        if last_updated == None:
            last_updated = {'num_location_phone_readings': 0, 'max_flavour_points_reading': 0, 'num_flavour_review_count_readings': 0, 'num_location_Countrycode_number_readings': 0, 'last_updated': '2020-02-16T16:18:47'}
            stats_list = [last_updated]
        else:
            last_updated = last_updated.to_dict()
            all_stats = session.query(Stats).order_by(Stats.last_updated.desc()).all()
            stats_list = []
            for stat in all_stats:
                stats_list.append(stat.to_dict())
    else:
        last_updated = {'num_location_phone_readings': 0, 'max_flavour_points_reading': 0, 'num_flavour_review_count_readings': 0, 'num_location_Countrycode_number_readings': 0, 'last_updated': '2020-02-16T16:18:47'}

    orders_data = requests.get(f"{app_config['eventstore']['url']}/coffee/flavour", params = {"timestamp": last_updated["last_updated"]})
    deliveries_data = requests.get(f"{app_config['eventstore']['url']}/coffee/location", params = {"timestamp": last_updated["last_updated"]})

    if orders_data.status_code and deliveries_data.status_code == 200:
        logger.info(f"Data received! {len(orders_data.json())} orders received, {len(deliveries_data.json())} deliveries received")
        for order in orders_data.json():
            logger.debug(f"Order data: {order['traceID']} received")
        for delivery in deliveries_data.json():
            logger.debug(f"Delivery data: {delivery['traceID']} received")

        num_location_phone_readings = last_updated["num_location_phone_readings"] + len(orders_data.json()) # Calculate stats

        max_flavour_points_reading = last_updated["max_flavour_points_reading"]  + len(deliveries_data.json())

        num_flavour_review_count_readings = last_updated['num_flavour_review_count_readings']
        for order in orders_data.json():
            if order['Flavour_points'] > num_flavour_review_count_readings:
                num_flavour_review_count_readings = order['Flavour_points']

        num_location_Countrycode_number_readings = last_updated['num_location_Countrycode_number_readings']
        for delivery in deliveries_data.json():
            if delivery['location_Countrycode_number'] > num_location_Countrycode_number_readings:
                num_location_Countrycode_number_readings = delivery['location_Countrycode_number']




        last_updated = current_date

        stats = Stats(num_location_phone_readings, max_flavour_points_reading, num_flavour_review_count_readings, num_location_Countrycode_number_readings, current_date)
        stats_dict = stats.to_dict()
        print(stats_dict)

        session.add(stats)
        session.commit()
        session.close()
        logger.info("Finished processing data")
    else:
        logger.error(f"Failed to receive data with error code: {orders_data.status_code} and {deliveries_data.status_code}")
    

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
