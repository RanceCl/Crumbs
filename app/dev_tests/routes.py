from flask import request, jsonify
from flask_cors import CORS

from ..models import Users, Orders, Customers, Cookies, Cookie_Inventory, Cookie_Orders
import psycopg2

from .. import db

from . import dev_tests


# ----------------------------------------- Dev Tests -----------------------------------------
def add_user(email, password, first_name, last_name):
    password_confirm = password
    new_user = Users(email=email, 
                     first_name=first_name, 
                     last_name=last_name)
    if not new_user.set_password(password, password_confirm):
        db.session.add(new_user)
        db.session.commit()
    return None

def add_order(customer_id, payment_id):
    new_order = Orders(customer_id=customer_id,
                       payment_id=payment_id)
    db.session.add(new_order)
    db.session.commit()
    return new_order.id

def add_customer(first_name, user_id):
    new_customer = Customers(first_name=first_name,
                            last_name=first_name,
                            user_id=user_id)
    #current_user.append(new_customer)
    db.session.add(new_customer)
    db.session.commit()
    return new_customer.id

@dev_tests.route('/populate_users', methods=['GET','POST'])
def populate_users():
    add_user("chadgregpaulthompson@gmail.com", "Ch@t3PT", "Chad", "GPT")
    add_user("anonymous@email.com", "S3cr3t P@$$word", "Anonymous", "NoLastName")
    add_user("known@email.com", "S33n P@$$word", "Known", "HasLastName")
    add_user("elmo@email.com", "B33G B1rd$", "Elmo", "Sesame")
    

    return "Table populated"
    # return redirect(url_for('login'))

# For each customer, add four orders
def populate_orders(customer_id):
    for _ in range(4):
        add_order(customer_id, 0)
    return None

@dev_tests.route('/populate_customers', methods=['GET','POST'])
def populate_customers():
    names = ["Chad","Jim","Known","Jane","Don","Abe","Corey","Linda","Leen","Noni","Chi-Chi","Best","Midnight","Marley","Known","Chad"]
    name_index = 0
    user_ids = [id[0] for id in Users.query.with_entities(Users.id).all()]
    for user_id in user_ids:
        # Add three names to the current user.
        for _ in range(3):
            if name_index >= len(names):
                # Stop adding customers if we've used all of the names.
                return "Customers populated"
            
            new_customer_id = add_customer(names[name_index], user_id)
            populate_orders(new_customer_id)
            name_index += 1
            
    return "Customers populated"