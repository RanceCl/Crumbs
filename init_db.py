import os
import psycopg2

# Make sure database exists
def create_initial_db():
    conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="devcarolinaba")
    conn.autocommit = True

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Create a new database
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'crumbs_db'")
    exists = cur.fetchone()
    if not exists:
        cur.execute('CREATE DATABASE crumbs_db')
 
    conn.commit()
    cur.close()

# Connect to database
def connect_to_db():
    conn = psycopg2.connect(
            host="localhost",
            database="crumbs_db",
            user="postgres",
            password="devcarolinaba")
    return conn

def initial_setup(conn):
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Create a new table of users, customers and cookies
    cur.execute('DROP TABLE IF EXISTS users, customers, cookies;')
    cur.execute('CREATE TABLE users (id SERIAL PRIMARY KEY,'
                                    'username VARCHAR(50) NOT NULL,'
                                    'password VARCHAR(20) NOT NULL,'
                                    'date_added DATE DEFAULT CURRENT_TIMESTAMP);'
                                    )
    cur.execute('CREATE TABLE customers (id SERIAL PRIMARY KEY,'
                                    'customer_name VARCHAR(255) NOT NULL,'
                                    'customer_test_id SMALLINT NOT NULL,'
                                    'date_added DATE DEFAULT CURRENT_TIMESTAMP);'
                                    )
    
    cur.execute('CREATE TABLE cookies (id SERIAL PRIMARY KEY,'
                                    'cookie_name VARCHAR(50) NOT NULL,'
                                    'picture_id SMALLINT NOT NULL);'
                                    )

    # Insert data into the table
    # Populate users
    cur.executemany(
        'INSERT INTO users (username, password)'
        'VALUES (%s, %s)',
        [('Chad Greg Paul Thompson', 'ChatGPT'),
         ('Anonymous NoLastName', 'SecretPassword'),
         ('Know HasLastName', 'SeenPassword')
         ]
         )
    
     # Populate customers
    cur.executemany(
        'INSERT INTO customers (customer_name, customer_test_id)'
        'VALUES (%s, %s)',
        [('Leanne', 3),
         ('Dave', 1),
         ('Dave Again', 9)
         ]
         )
        
     # Populate cookies
    cur.executemany(
        'INSERT INTO cookies (cookie_name, picture_id)'
        'VALUES (%s, %s)',
        [('Lemonades', 3),
         ('Adventurefuls', 1),
         ('Caramel Chocolate Chip', 9)
         ]
         )

    conn.commit()
    cur.close()

def create_table():
    create_initial_db()
    conn = connect_to_db()
    initial_setup(conn)
    conn.close()

