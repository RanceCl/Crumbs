from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Users, Orders, Customers, Cookies, Cookie_Inventory, Order_Cookies
import psycopg2

from .. import db, login_manager

from . import orders

# ----------------------------------------- Orders -----------------------------------------
def order_retriever(order_id, customer_id):
    if customer_id:
        return Orders.query.join(Customers).filter(Customers.id==customer_id, Orders.id==order_id).first()
    return Orders.query.join(Customers).filter(Orders.id==order_id).first()



# Retrieve orders 
@orders.route('/', methods=['GET'])
@login_required
def get_orders_list(customer_id=None):
    # If sent from customer, query based on customer id as well.
    if customer_id:
        orders = Orders.query.join(Customers).filter_by(id=customer_id, user_id=current_user.id).all()
    else:
        orders = Orders.query.join(Customers).filter_by(user_id=current_user.id).all()
    result = []
    for order in orders:
        result.append(order.to_dict())
    return {"orders": result}, 200

# Add order from order page
@orders.route('/', methods=['POST'])
@login_required
def add_order(customer_id=None):
    if (('customer_id' in request.form or customer_id)
        and 'payment_id' in request.form):
        customer_id = request.form.get("customer_id", customer_id)
        payment_id = request.form.get("payment_id")
        customer = Customers.query.filter_by(id=customer_id).first()
        # Make sure customer exists before making an order for them.
        if not customer:
            return "I'm sorry, customer with" + customer_id + " doesn't exist. Please create a customer and try again."
        
        order = Orders(customer_id=customer_id,payment_id=payment_id)
        db.session.add(order)
        db.session.commit()
        return order.to_dict()
    return "Please fill out the form!"

# Show orders based on id.
@orders.route('/<id>', methods=['GET'])
@login_required
def read_order(id, customer_id=None):
    order = order_retriever(id, customer_id)
    if not order:
        return "I'm sorry, you don't have an order with id " + id + ". :("
    return order.to_dict()

# Update orders based on id.
@orders.route('/<id>', methods=['PATCH'])
@login_required
def update_order(id, customer_id=None):
    order = order_retriever(id, customer_id)
    if not order:
        return "I'm sorry, you don't have an order with id " + id + ". :("
    order.customer_id = request.form.get("customer_id", order.customer_id) # If no customer_id provided, no change
    order.payment_id = request.form.get("payment_id", order.payment_id)
    db.session.commit()
    return order.to_dict()

# Delete orders based on id.
@orders.route('/<id>', methods=['DELETE'])
@login_required
def delete_order(id, customer_id=None):
    # If sent from customer, query based on customer id instead.
    if customer_id:
        order = Orders.query.filter_by(id=id, customer_id=customer_id).first()
    else:
        order = Orders.query.filter_by(id=id).first()
    if not order:
        return id + " doesn't exist for you. :("
    db.session.delete(order)
    db.session.commit()
    return id + " deleted! :D"
