from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Users, Orders, Customers, Cookies, Cookie_Inventory, Cookie_Orders
import psycopg2

from .. import db

from . import customers

from ..orders.routes import get_orders_list, add_order, read_order, update_order, delete_order


# ----------------------------------------- Customers -----------------------------------------
# Retrieve customers
@customers.route('/', methods=['GET'])
@login_required
def get_customer_list():
    # User.query.join(Skill).filter(Skill.skill == skill_name).all()
    customers = Customers.query.filter_by(user_id=current_user.id).all()
    result = []
    for customer in customers:
        result.append({
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            'user_id': customer.user_id
        })
    return {"customers": result}, 200

# Create customer
@customers.route('/', methods=['POST'])
@login_required
def add_customer():
    if ('first_name' in request.form
        and 'last_name' in request.form):
        first_name=request.form.get("first_name")
        last_name=request.form.get("last_name")
        new_customer = Customers(first_name=first_name,
                                 last_name=last_name,
                                 user_id=current_user.id)
        db.session.add(new_customer)
        db.session.commit()

        return first_name + " " + last_name + " added as a customer!"
    return "Please fill out the form!"

# Show customers based on id.
@customers.route('/<id>', methods=['GET'])
@login_required
def read_customer(id):
    customer = Customers.query.filter_by(id=id, user_id=current_user.id).first()
    if not customer:
        return "I'm sorry, a customer " + id + " doesn't belong to you. :("
    return {'id': customer.id, 
            'first_name': customer.first_name, 
            'last_name': customer.last_name, 
            'user_id': customer.user_id}

# Update customers based on id.
@customers.route('/<id>', methods=['PATCH'])
@login_required
def update_customer(id):
    if ('first_name' in request.form
        and 'last_name' in request.form):
        customer = Customers.query.filter_by(id=id, user_id=current_user.id).first()
        if not customer:
            return "I'm sorry, a customer " + id + " doesn't belong to you. :("
        customer.first_name =request.form.get("first_name")
        customer.last_name =request.form.get("last_name")
        db.session.commit()
        return {'id': customer.id, 
                'first_name': customer.first_name, 
                'last_name': customer.last_name, 
                'user_id': customer.user_id}
    return "Please fill out the form!"

# Delete customers based on id.
@customers.route('/<id>', methods=['DELETE'])
@login_required
def delete_customer(id):
    customer = Customers.query.filter_by(id=id, user_id=current_user.id).first()
    if not customer: 
        return id + " doesn't exist. :("
    db.session.delete(customer)
    db.session.commit()
    return id + " deleted! :D"


# Show customer orders based on id.
@customers.route('/<id>/orders', methods=['GET'])
@login_required
def read_customer_orders(id):
    return get_orders_list(customer_id=id)

# Add order to customer
@customers.route('/<id>/orders', methods=['POST', 'PATCH'])
@login_required
def add_customer_order(id):
    return add_order(customer_id=id)

# Show customer order based on id.
@customers.route('/<id>/orders/<order_id>', methods=['GET'])
@login_required
def read_customer_order(id, order_id):
    return read_order(order_id, customer_id=id)

# Update customer orders based on id.
@customers.route('/<id>/orders/<order_id>', methods=['PATCH'])
@login_required
def update_customer_order(id, order_id):
    return update_order(order_id, customer_id=id)

# Delete customer orders based on id.
@customers.route('/<id>/orders/<order_id>', methods=['DELETE'])
@login_required
def delete_customer_order(id, order_id):
    return delete_order(order_id, customer_id=id)
