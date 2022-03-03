import mysql.connector
import yaml

""" Read app_conf.yml """
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

user = app_config.get("datastore")["user"]
password = app_config.get("datastore")["password"]
hostname = app_config.get("datastore")["hostname"]
port = app_config.get("datastore")["port"]
db = app_config.get("datastore")["db"]

conn = mysql.connector.connect(host=hostname,
                               user=user, password=password, database=db)


c = conn.cursor()
c.execute('''
          CREATE TABLE coffeeLocation
          (id INT NOT NULL AUTO_INCREMENT, 
           location_id VARCHAR(250) NOT NULL,
           location_name VARCHAR(250) NOT NULL,
           location_phone_number BIGINT NOT NULL,
           location_Countrycode_number INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT coffeeLocation_pk PRIMARY KEY(id)
           )
          ''')

c.execute('''
          CREATE TABLE coffeeFlavour
          (id INT NOT NULL AUTO_INCREMENT, 
           coffee_id VARCHAR(250) NOT NULL,
           coffee_name VARCHAR(250) NOT NULL,
           Flavour_points INTEGER NOT NULL,
           Flavour_review_count INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL, 
           CONSTRAINT coffeeFlavour_pk PRIMARY KEY(id))
          ''')

conn.commit()
conn.close()
