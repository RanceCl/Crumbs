from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Customers
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
        result.append(customer.to_dict())
    return {"customers": result}, 200

# Create customer
@customers.route('/', methods=['POST'])
@login_required
def add_customer():
    # Input is a json.
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    # Can only add a customer if the proper information is given.
    if ('first_name' in data
        and 'last_name' in data):
        first_name=data.get("first_name")
        last_name=data.get("last_name")
        new_customer = Customers(first_name=first_name,
                                 last_name=last_name,
                                 user_id=current_user.id)
        # Validate and set email if one is present
        if 'email' in data:
            new_customer.set_email(data.get("email").strip().lower())
        
        db.session.add(new_customer)
        db.session.commit()

        return jsonify({"message": first_name + " " + last_name + " added as a customer!"}), 200
    return jsonify({'status': 'error', 'message': 'Please fill out the form!'}), 400

# Show customers based on id.
@customers.route('/<customer_id>', methods=['GET'])
@login_required
def read_customer(customer_id):
    customer = Customers.query.filter_by(id=customer_id, user_id=current_user.id).first()
    if not customer:
        return jsonify({"message": "Customer " + customer_id + " not found."}), 404
    return jsonify(customer.to_dict()), 200

# Update customers based on id.
@customers.route('/<customer_id>', methods=['PATCH'])
@login_required
def update_customer(customer_id):
    # Input is a json.
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    customer = Customers.query.filter_by(id=customer_id, user_id=current_user.id).first()
    if not customer:
        return jsonify({"message": "Customer " + customer_id + " not found."}), 404
    
    # Change the names if provided
    if 'first_name' in data: 
        customer.first_name = data.get("first_name")
    if 'last_name' in data:
        customer.last_name = data.get("last_name")
    if 'email' in data:
            customer.set_email(data.get("email").strip().lower())
    
    db.session.commit()
    return jsonify(customer.to_dict()), 200

# Delete customers based on id.
@customers.route('/<customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    customer = Customers.query.filter_by(id=customer_id, user_id=current_user.id).first()
    if not customer: 
        return jsonify({"message": "Customer " + customer_id + " not found."}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer " + customer_id + " deleted."}), 200


# Show customer orders based on id.
@customers.route('/<customer_id>/orders', methods=['GET'])
@login_required
def read_customer_orders(customer_id):
    return get_orders_list(customer_id=customer_id)

# Add order to customer
@customers.route('/<customer_id>/orders', methods=['POST'])
@login_required
def add_customer_order(customer_id):
    return add_order(customer_id=customer_id)

# Show customer order based on id.
@customers.route('/<customer_id>/orders/<order_id>', methods=['GET'])
@login_required
def read_customer_order(customer_id, order_id):
    return read_order(order_id, customer_id=customer_id)

# Update customer orders based on id.
@customers.route('/<customer_id>/orders/<order_id>', methods=['PATCH'])
@login_required
def update_customer_order(customer_id, order_id):
    return update_order(order_id, customer_id=customer_id)

# Delete customer orders based on id.
@customers.route('/<customer_id>/orders/<order_id>', methods=['DELETE'])
@login_required
def delete_customer_order(customer_id, order_id):
    return delete_order(order_id, customer_id=customer_id)
