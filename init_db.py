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

# Connect to database
def connect_to_db():
    conn = psycopg2.connect(
            host=os.environ["POSTRGRES_HOST"],
            database=os.environ["POSTRGRES_DATABASE"],
            user=os.environ["POSTRGRES_USER"],
            password=os.environ["POSTRGRES_PASSWORD"])
    return conn

# Creating the tables
def table_setup(conn):
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Create a new table of user, customer and cookie
    cur.execute("DROP TABLE IF EXISTS users, customer, cookies, orders, carted_cookies;")
    
    # Table for users
    cur.execute(
        "CREATE TABLE users (id SERIAL PRIMARY KEY,"
        "email VARCHAR(255) UNIQUE NOT NULL,"
        "password_hash VARCHAR(255) NOT NULL,"
        "first_name VARCHAR(255) NOT NULL,"
        "last_name VARCHAR(255) NOT NULL,"
        "date_added DATE DEFAULT CURRENT_TIMESTAMP);"
    )
    
    # Table for cookies
    cur.execute(
        "CREATE TABLE cookies (id SMALLSERIAL PRIMARY KEY,"
        "cookie_name VARCHAR(50) NOT NULL,"
        "description VARCHAR(255) NOT NULL DEFAULT '',"
        "price FLOAT NOT NULL DEFAULT 0,"
        "picture_url VARCHAR(255) NOT NULL DEFAULT '');"
    )

    # Table for cookie inventory
    cur.execute(
        "CREATE TABLE cookie_inventory (user_id INT NOT NULL,"
        "cookie_id SMALLINT NOT NULL,"
        "inventory INT NOT NULL DEFAULT 0,"
        "PRIMARY KEY (user_id, cookie_id),"
        "FOREIGN KEY (user_id) REFERENCES users(id),"
        "FOREIGN KEY (cookie_id) REFERENCES cookies(id));"
    )
    
    # Table for customers
    cur.execute(
        "CREATE TABLE customers (id SERIAL PRIMARY KEY,"
        "first_name VARCHAR(255) NOT NULL,"
        "last_name VARCHAR(255) NOT NULL,"
        "user_id INT NOT NULL,"
        "FOREIGN KEY (user_id) REFERENCES users(id));"
    )

    # Table for order
    cur.execute(
        "CREATE TABLE orders (id SERIAL PRIMARY KEY,"
        "customer_id INT NOT NULL,"
        "payment_id INT NOT NULL,"
        "cost INT NOT NULL DEFAULT 0,"
        "date_added DATE DEFAULT CURRENT_TIMESTAMP,"
        "FOREIGN KEY (customer_id) REFERENCES customers(id));"
    )

    # Table for specific cookie amounts in an order
    cur.execute(
        "CREATE TABLE order_cookies (order_id INT NOT NULL,"
        "cookie_id INT NOT NULL,"
        "quantity INT NOT NULL DEFAULT 0,"
        "cost INT NOT NULL DEFAULT 0,"
        "PRIMARY KEY (order_id, cookie_id),"
        "FOREIGN KEY (order_id) REFERENCES orders(id),"
        "FOREIGN KEY (cookie_id) REFERENCES cookies(id));"
    )

    '''
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

    # Populate cookies
    cur.executemany(
        "INSERT INTO cookies (cookie_name, price, description, picture_url)"
        "VALUES (%s, %s, %s, %s)",
        [("Adventurefuls", 6,
          "Indulgent brownie-inspired cookies topped with caramel flavored crème with a hint of sea salt.",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage.coreimg.png/1693317691596/meetthecookies-graphics-hybridadventurefuls-255x255.png"),
         ("Caramel Chocolate Chip", 6, 
          "Gluten free! Chewy cookies with rich caramel, semisweet chocolate chips, and a hint of sea salt.",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy.coreimg.png/1688655459226/21-marcomm-meetthecookies-graphics-abccaramelchocolatechip-255x255.png"),
         ("Caramel deLites", 6, 
          "Crisp cookies with caramel, coconut, and chocolaty stripes .",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1168943426.coreimg.png/1693315719665/meetthecookies-graphics-hybridsamoascarameldelites-255x255.png"),
         ("Peanut Butter Sandwich | Do-si-dos", 6, 
          "Crunchy oatmeal sandwich cookies with peanut butter filling.",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1034315555.coreimg.png/1725455442556/meetthecookies-graphics-hybridpeanutbuttersandwichdosidos-255x255.png"),
         ("Girl Scout S'mores", 6, 
          "Crunchy graham sandwich cookies with chocolate and marshmallow filling.",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1756629764.coreimg.png/1693315770522/meetthecookies-graphics-lbbsmores-255x255.png"),
         ("Lemonades", 6, 
          "Savory, refreshing shortbread cookies topped with a tangy lemon-flavored icing.",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_973166062.coreimg.png/1688655543113/meetthecookies-graphics-abclemonades-255x255.png"),
         ("Lemon-Ups", 6, 
          "Crispy lemon cookies baked with inspiring messages.",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1787644668.coreimg.png/1693315792917/meetthecookies-graphics-lbblemonups-255x255.png"),
         ("Peanut Butter Patties", 6, 
          "Crispy cookies layered with peanut butter and covered with a chocolaty coating.",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_435681049.coreimg.png/1693315815634/meetthecookies-graphics-hybridpeanutbutterpattiestagalongs-255x255.png"),
         ("Thin Mints", 6, 
          "Crisp, chocolate cookies dipped in a delicious mint chocolaty coating.",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1574458209.coreimg.png/1693315839299/meetthecookies-graphics-hybridthinmints-255x255.png"),
         ("Toast-Yays", 6, 
          "Yummy toast-shaped cookies full of French toast flavor and dipped in delicious icing.",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1639980537.coreimg.png/1693230514183/meetthecookies-graphics-abctoast-yay-255x255.png"),
         ("Toffee-tastic", 6, 
          "Gluten free! Rich, buttery cookies with sweet, crunchy toffee bits.",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1157222513.coreimg.png/1693316248715/meetthecookies-graphics-lbbtoffeetastic-255x255.png"),
         ("Trefoils", 6, 
          "Iconic shortbread cookies inspired by the original Girl Scout Cookie recipe.",
          "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_750886972.coreimg.png/1713984333162/meetthecookies-graphics-hybridshortbreadtrefoils-255x255.png")]
    )
    '''
    # Insert data into the table
    # Populate users
    cur.executemany(
        "INSERT INTO users (email, password_hash)"
        "VALUES (%s, %s)",
        [("Chad Greg Paul Thompson", "ChatGPT"),
         ("Anonymous NoLastName", "SecretPassword"),
         ("Know HasLastName", "SeenPassword")]
    )
    '''
    '''
    # Populate customers
    cur.executemany(
        "INSERT INTO customer (first_name, last_name, user_id)"
        "VALUES (%s, %s, %s)",
        [("Leanne", "Lee", 3),
         ("Dave", "", 1),
         ("Dave", "Again", 2)]
    )
        
    # Populate cookie
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

