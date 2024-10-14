import os
import sys
import psycopg2
import load_env_var
#from load_env_var import pgBase

# Make sure database exists.
def create_initial_db():
    conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user=os.environ["POSTRGRES_USER"],
            password=os.environ["POSTRGRES_PASSWORD"])
    conn.autocommit = True

    # Open a cursor to perform database operations.
    cur = conn.cursor()

    # Reset Database if indicated to
    if (len(sys.argv)==2) and (sys.argv[1] == "reset"):
        cur.execute("DROP DATABASE IF EXISTS crumbs_db")
    
    # Create a new database if one doesn"t.
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'crumbs_db'")
    exists = cur.fetchone()
    if not exists:
        cur.execute("CREATE DATABASE crumbs_db")
    
    conn.commit()
    cur.close()


create_initial_db()


