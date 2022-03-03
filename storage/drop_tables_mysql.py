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
          DROP TABLE coffeeLocation, coffeeFlavour
          ''')

conn.commit()
conn.close()
