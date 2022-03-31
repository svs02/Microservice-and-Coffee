import connexion
import logging.config
import requests
import yaml
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS
from base import Base
from stats import Stats
import os
import os.path
from os import path
from create_database import create_database

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('processing')
logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)

def check_data():
    file_exists = os.path.exists(f'{app_config["datastore"]["filename"]}')
    if file_exists:
        logger.info(f'log path is {app_config["datastore"]["filename"]}')
        logger.info("data.sqlite is exist")
    else:
        logger.info("data.sqlite is not exist")
        create_database()
        logger.info("create data.sqlite")

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_stats():
    """ Gets the temperature and fan speed events stats  """
    session = DB_SESSION()
    logger.info("Start Get Stats request")
    stats = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    if not stats:
        logger.debug(f'No latest statistics found')
        return "Statistics do not exist", 404
    stats = stats.to_dict()
    session.close()
    logger.debug(f'The latest statistics is {stats}')
    logger.info("Get Stats request done")
    return stats, 200


def populate_stats(dictionary=None):
    session = DB_SESSION()
    logger.info("Starting pop_stats")
    stats = session.query(Stats).order_by(Stats.id.desc()).first()
    if not stats:
        stats = {
            "id": 0,
            "num_location_phone_readings": 0,
            "max_flavour_points_reading": 0,
            "num_flavour_review_count_readings": 0,
            "num_location_Countrycode_number_readings": 0,
            "last_updated": datetime.datetime.now()
        }
    logger.info(stats)
    if not isinstance(stats, dict):
        stats = stats.to_dict()

    new_stats = {
        "id": 0,
        "num_location_phone_readings": 0,
        "max_flavour_points_reading": 0,
        "num_flavour_review_count_readings": 0,
        "num_location_Countrycode_number_readings": 0,
        "last_updated": datetime.datetime.now()
    }

    start_timestamp = stats['last_updated']
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

        new_stats['num_location_phone_readings'] = stats['num_location_phone_readings'] + len(location_response_data)/2
        new_stats['num_location_Countrycode_number_readings'] = stats['num_location_Countrycode_number_readings'] + len(location_response_data)/2

        max_phone_readings = new_stats['num_location_phone_readings']
        max_Countrycode_number_readings = new_stats['num_location_Countrycode_number_readings']
        for i in location_response_data:
            max_phone_readings = max(max_phone_readings, i['num_location_phone_readings'])
            max_Countrycode_number_readings = max(max_Countrycode_number_readings, i['num_location_Countrycode_number_readings'])

        new_stats['num_location_phone_readings'] = max_phone_readings
        new_stats['num_location_Countrycode_number_readings'] = max_Countrycode_number_readings

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

        new_stats['max_flavour_points_reading'] = stats['max_flavour_points_reading'] + len(flavour_response_data)/2
        new_stats['num_flavour_review_count_readings'] = stats['num_flavour_review_count_readings'] + len(flavour_response_data)/2

        max_flavour_points_reading = new_stats['max_flavour_points_reading']
        num_flavour_review_count_readings = new_stats['num_flavour_review_count_readings']
        for i in flavour_response_data:
            max_flavour_points_reading = max(max_flavour_points_reading, i['max_flavour_points_reading'])
            num_flavour_review_count_readings = max(num_flavour_review_count_readings, i['num_flavour_review_count_readings'])

        new_stats['max_flavour_points_reading'] = max_flavour_points_reading
        new_stats['num_flavour_review_count_readings'] = num_flavour_review_count_readings

    add_stats = Stats(new_stats["num_location_phone_readings"], new_stats["max_flavour_points_reading"],
                      new_stats["num_flavour_review_count_readings"], new_stats["num_location_Countrycode_number_readings"], new_stats["last_updated"])

    session.add(add_stats)
    session.commit()
    session.close()

    logger.debug(f"Processing data has been done. {new_stats}")
    logger.info(f"Periodic Processing Ends")
    return



def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(check_data, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()



app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('openapi.yaml', base_path="/processing", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    check_data()
    init_scheduler()
    app.run(port=8100, use_reloader=False)
