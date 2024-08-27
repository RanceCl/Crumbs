import sys
import psycopg2

# Make sure database exists.
def create_initial_db():
    conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="postgres")
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

# Connect to database
def connect_to_db():
    conn = psycopg2.connect(
            host="localhost",
            database="crumbs_db",
            user="postgres",
            password="postgres")
    return conn

# Creating the tables
def table_setup(conn):
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Create a new table of users, customers and cookies
    cur.execute("DROP TABLE IF EXISTS users, customers, cookies, orders, carted_cookies;")
    
    # Table for users
    cur.execute(
        "CREATE TABLE users (id SERIAL PRIMARY KEY,"
        "email VARCHAR(255) UNIQUE NOT NULL,"
        "password VARCHAR(255) NOT NULL,"
        "date_added DATE DEFAULT CURRENT_TIMESTAMP);"
    )
    '''
    # Table for customers
    cur.execute(
        "CREATE TABLE customers (id SERIAL PRIMARY KEY,"
        "first_name VARCHAR(255) NOT NULL,"
        "last_name VARCHAR(255) NOT NULL,"
        "user_id INT NOT NULL,"
        "date_added DATE DEFAULT CURRENT_TIMESTAMP);"
    )

    # Table for cookies
    cur.execute(
        "CREATE TABLE cookies (id SERIAL PRIMARY KEY,"
        "cookie_name VARCHAR(50) NOT NULL,"
        "description VARCHAR(255) NOT NULL DEFAULT '',"
        "price FLOAT NOT NULL DEFAULT 0,"
        "inventory_count INT NOT NULL DEFAULT 0,"
        "picture_id SMALLINT NOT NULL);"
    )

    # Table for orders
    cur.execute(
        "CREATE TABLE orders (id SERIAL PRIMARY KEY,"
        "customer_id INT NOT NULL,"
        "total INT NOT NULL DEFAULT 0);"
    )
    
    # Table for carted cookies
    cur.execute(
        "CREATE TABLE carted_cookies (order_id INT NOT NULL,"
        "cookie_id INT NOT NULL,"
        "status VARCHAR(255) NOT NULL DEFAULT 'On hold.',"
        "sub_total INT NOT NULL DEFAULT 0,"
        "PRIMARY KEY (order_id, cookie_id));"
    )
    '''
    
    conn.commit()
    cur.close()

# Populate the table with test data.
def table_populate(conn):
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Insert data into the table
    # Populate users
    cur.executemany(
        "INSERT INTO users (email, password)"
        "VALUES (%s, %s)",
        [("Chad Greg Paul Thompson", "ChatGPT"),
         ("Anonymous NoLastName", "SecretPassword"),
         ("Know HasLastName", "SeenPassword")]
    )
    '''
    # Populate customers
    cur.executemany(
        "INSERT INTO customers (first_name, last_name, user_id)"
        "VALUES (%s, %s, %s)",
        [("Leanne", "Lee", 3),
         ("Dave", "", 1),
         ("Dave", "Again", 2)]
    )
        
     # Populate cookies
    cur.executemany(
        "INSERT INTO cookies (cookie_name, picture_id)"
        "VALUES (%s, %s)",
        [("Adventurefuls", 1),
         ("Caramel Chocolate Chip", 2),
         ("Caramel deLites", 3),
         ("Do-si-dos", 4),
         ("Girl Scout Smores", 5),
         ("Lemonades", 6),
         ("Lemon-Ups", 7),
         ("Peanut Butter Patties", 8),
         ("Thin Mints", 9),
         ("Toast-Yays", 10),
         ("Toffee-tastic", 11),
         ("Trefoils", 12)]
    )
    '''
    conn.commit()
    cur.close()

def initial_setup(conn):
    table_setup(conn)
    table_populate(conn)

create_initial_db()
conn = connect_to_db()
initial_setup(conn)
conn.close()

