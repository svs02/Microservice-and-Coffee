import sqlite3

def create_database():
    conn = sqlite3.connect('/data/health.sqlite')
    c = conn.cursor()
    c.execute('''
                CREATE TABLE health
                (id INTEGER PRIMARY KEY ASC,
                receiver VARCHAR(100) NOT NULL,
                storage VARCHAR(100) NOT NULL,
                processing VARCHAR(100) NOT NULL,
                audit_log VARCHAR(100) NOT NULL,
                last_updated VARCHAR(100) NOT NULL)
            ''')
    conn.commit()
    conn.close()

