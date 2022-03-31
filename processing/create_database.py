import sqlite3

def create_database():
    conn = sqlite3.connect('/data/data.sqlite')
    c = conn.cursor()
    c.execute('''
              CREATE TABLE stats
              (id INTEGER PRIMARY KEY ASC, 
               num_location_phone_readings INTEGER NOT NULL,
               max_flavour_points_reading INTEGER,
               num_flavour_review_count_readings INTEGER NOT NULL,
               num_location_Countrycode_number_readings INTEGER NOT NULL,
               last_updated VARCHAR(100) NOT NULL
               )
              ''')
    conn.commit()
    conn.close()
    print("database made")




