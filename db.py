import sys
import psycopg2

# Connect to database
def connect_to_db():
    conn = psycopg2.connect(
            host="localhost",
            database="crumbs_db",
            user="postgres",
            password="postgres")
    return conn

# Adding a user
def create_user(conn, input_email, input_password):
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Insert data into the table
    cur.execute(
        "INSERT INTO users (email, password)"
        "VALUES (%s, %s)",
        (input_email, input_password)
    )
    
    conn.commit()
    cur.close()

# Read a user
def read_user(conn, input_email, input_password):
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Select data from the table
    cur.execute(
        "SELECT * FROM users WHERE "
        "email = %s AND password = %s",
        (input_email, input_password)
    )

    user_info = cur.fetchone()
    if user_info:
        print(user_info)
    else: 
        print("No user with this username and password found.")
    
    conn.commit()
    cur.close()

# Update a user's email
def update_email(conn, input_email, input_password, new_email):
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Select data from the table
    cur.execute(
        "UPDATE users SET "
        "email = %s WHERE "
        "email = %s AND password = %s",
        (new_email, input_email, input_password)
    )

    conn.commit()
    cur.close()

# Update a user's password
def update_password(conn, input_email, input_password, new_password):
    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Select data from the table
    cur.execute(
        "UPDATE users SET "
        "password = %s WHERE "
        "email = %s AND password = %s",
        (new_password, input_email, input_password)
    )
    
    conn.commit()
    cur.close()

# Deleting a user
def delete_user(conn, input_email, input_password):
    # Open a cursor to perform database operations
    cur = conn.cursor()
    
    # Delete only user with the same username AND password
    cur.execute(
        "DELETE FROM users WHERE "
        "email = %s AND password = %s",
        (input_email, input_password)
    )
    
    conn.commit()
    cur.close()

# Test CRUD operations for users.
if (len(sys.argv)!=4):
    print("Not enough inputs given, must be in the format of:")
    print("python db.py [create, read, update_email, update_password, delete] [email] [password]")
    exit(1)
conn = connect_to_db()

match sys.argv[1]:
    case "create":
        create_user(conn, sys.argv[2], sys.argv[3])
    case "read":
        read_user(conn, sys.argv[2], sys.argv[3])
    case "update_email":
        new_email = input("Enter a new email: ")
        update_email(conn, sys.argv[2], sys.argv[3], new_email)
    case "update_password":
        new_password = input("Enter a new password: ")
        update_password(conn, sys.argv[2], sys.argv[3], new_password)
    case "delete":
        delete_user(conn, sys.argv[2], sys.argv[3])

conn.close()

