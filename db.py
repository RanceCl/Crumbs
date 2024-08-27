import psycopg2
from psycopg2.extras import RealDictCursor

# Connect to database
def connect_to_db():
    conn = psycopg2.connect(
            host="localhost",
            database="crumbs_db",
            user="postgres",
            password="postgres",
            cursor_factory=RealDictCursor)
    return conn

# Make sure data is present
def row_filled(row):
    if row:
        return dict(row)
    else: 
        return ('', 204)


# Registering a user
def user_register(email, password):
    # Connect to database
    conn = connect_to_db()

    # Open a cursor to perform database operations
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE "
        "email = %s",
        (email,)
    )
    account_exists = cur.fetchone()

    if account_exists: 
        message = "Account with this email already exists!"
    else:

        # Insert data into the table
        cur.execute(
            "INSERT INTO users (email, password)"
            "VALUES (%s, %s) "
            "RETURNING *",
            (email, password)
        )
        row = cur.fetchone()
        message = row_filled(row)
    conn.commit()
    cur.close()
    conn.close()
    return message

# Logging a user in
def user_login(email, password):
    # Connect to database
    conn = connect_to_db()

    # Open a cursor to perform database operations
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE "
        "email = %s AND password = %s",
        (email, password)
    )
    user = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()
    return user

# Adding a user
def user_create(input_email, input_password):
    # Connect to database
    conn = connect_to_db()

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Insert data into the table
    cur.execute(
        "INSERT INTO users (email, password)"
        "VALUES (%s, %s) "
        "RETURNING *",
        (input_email, input_password)
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return row_filled(row)

# Read a user's information
def user_read_by_id(id):
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE "
        "id = %s",
        (id,)
    )
    row = cur.fetchone()
    
    conn.commit()
    cur.close()
    conn.close()

    # Make sure to only return information if present.
    return row_filled(row)

# Update a user's account
def user_update_by_id(id, new_email, new_password):
    conn = connect_to_db()
    cur = conn.cursor()

    # Select data from the table
    cur.execute(
        "UPDATE users SET "
        "email = %s, password = %s WHERE "
        "id = %s"
        "RETURNING *",
        (new_email, new_password, id)
    )
    
    row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()
    return row_filled(row)

# Update a user's email
def user_update_email(input_email, input_password, new_email):
    conn = connect_to_db()
    cur = conn.cursor()

    # Select data from the table
    cur.execute(
        "UPDATE users SET "
        "email = %s WHERE "
        "email = %s AND password = %s"
        "RETURNING *",
        (new_email, input_email, input_password)
    )
    row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()
    return row_filled(row)

# Update a user's password
def user_update_password(input_email, input_password, new_password):
    conn = connect_to_db()
    cur = conn.cursor()

    # Select data from the table
    cur.execute(
        "UPDATE users SET "
        "password = %s WHERE "
        "email = %s AND password = %s"
        "RETURNING *",
        (new_password, input_email, input_password)
    )
    row = cur.fetchone()
    
    conn.commit()
    cur.close()
    conn.close()
    return row_filled(row)

# Deleting a user
# Read a user's information
def user_delete_by_id(id):
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM users WHERE "
        "id = %s",
        (id,)
    )
    
    conn.commit()
    cur.close()
    conn.close()
    return {"Message": "User is eliminated."}
