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
from health import Health
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
logger = logging.getLogger('health')
logger.info("App Conf File: %s" % app_conf_file) 
logger.info("Log Conf File: %s" % log_conf_file)

def check_data():
    file_exists = os.path.exists(f'{app_config["datastore"]["filename"]}')
    if file_exists:
        logger.info(f'log path is {app_config["datastore"]["filename"]}')
        logger.info("health.sqlite is exist")
    else:
        logger.info("health.sqlite is not exist")
        create_database()
        logger.info("create health.sqlite")

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def get_health():
    """ Gets service health """
    session = DB_SESSION()
    logger.info("Start Get health request")
    health = session.query(Health).order_by(Health.last_updated.desc()).first()
    if not health:
        logger.debug(f'No latest statistics found')
        return "Statistics do not exist", 404
    health = health.to_dict()
    session.close()
    logger.debug(f'The latest statistics is {health}')
    logger.info("Get Health request done")
    return health, 200



def populate_health():
    session = DB_SESSION()
    logger.info("Starting populate_health")
    health = session.query(Health).order_by(Health.last_updated.desc()).first()

    if not health:
        health = {
            "receiver": "Down",
            "storage": "Down",
            "processing": "Down",
            "audit_log": "Down",
            "last_updated": datetime.datetime.now()
        }

    if not isinstance(health, dict):
        health = health.to_dict()

    new_health = {
        "receiver": "Down",
        "storage": "Down",
        "processing": "Down",
        "audit_log": "Down",
        "last_updated": datetime.datetime.now()
    }


    for service in app_config["eventurl"]:
        maxtime = app_config["response"]['period_sec']
        health = requests.get(app_config["eventurl"][f"{service}"] + "/health", timeout=maxtime)

        if health.status_code != 200:
            logger.error(f'{service} down')
        else:
            logger.info(f'{service} Running')
            new_health[f"{service}"] = 'Running'


    add_health = Health(
        new_health["receiver"],
        new_health["storage"],
        new_health["processing"],
        new_health["audit_log"],
        new_health["last_updated"]
    )


    session.add(add_health)
    session.commit()
    session.close()

    logger.debug(f"health data has been done. {new_health}")
    logger.info(f"Periodic health Ends")




def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(check_data, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.add_job(populate_health, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('openapi.yaml', base_path="/health", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)
