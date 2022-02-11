# Import modules
import psycopg2
import config as cfg


# DB Functions
def getCursor():
    conn = None
    try:
        # Connect to the Database
        conn = psycopg2.connect(
            host=cfg.sql['host'],
            user=cfg.sql['user'],
            password=cfg.sql['passw'],
            dbname=cfg.sql['db']
        )
        # Create a cursor
        cursor = conn.cursor()
        return cursor, conn

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
