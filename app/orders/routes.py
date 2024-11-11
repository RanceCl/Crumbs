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
    # Input is a json.
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    # A new order can only be placed if the customer id is provided and a valid payment type is also provided.
    if ('customer_id' in data or customer_id):
        customer_id = data.get("customer_id", customer_id)
        payment_type_name = data.get("payment_type_name", "Unspecified")
        customer = Customers.query.filter_by(id=customer_id).first()
        # Make sure customer exists before making an order for them.
        if not customer:
            return jsonify({"message": "Customer " + customer_id + " not found."}), 404
        
        order = Orders(
            customer_id=customer_id,
            payment_type=payment_type_name,
            notes=data.get("notes", "")
        )

        db.session.add(order)
        db.session.commit()
        return jsonify(order.to_dict()), 200
    return jsonify({'status': 'error', 'message': 'Please fill out the form!'}), 400

# Show orders based on id.
@orders.route('/<order_id>', methods=['GET'])
@login_required
def read_order(order_id, customer_id=None):
    order = order_retriever(order_id, customer_id)
    if not order:
        return jsonify({"message": "Order " + order_id + " not found."}), 404
    return jsonify(order.to_dict()), 200

# Update orders based on id.
@orders.route('/<order_id>', methods=['PATCH'])
@login_required
def update_order(order_id, customer_id=None):
    order = order_retriever(order_id, customer_id)
    if not order:
        return jsonify({"message": "Order " + order_id + " not found."}), 404
    
    # Change entry values if a change has been specified.
    # order.payment_type_name = request.form.get("payment_type_name", order.payment_type_name)
    # order.payment_status = request.form.get("payment_status", order.payment_status)
    # order.delivery_status = request.form.get("delivery_status", order.delivery_status)
    # order.order_status = request.form.get("order_status", order.order_status)
    # order.notes = request.form.get("notes", order.notes)

    # Input is a json.
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    # Change entry values if a change has been specified.
    if 'payment_type_name' in data:
        order.payment_type_name(data.get("payment_type_name"))
    order.payment_status = data.get("payment_status", order.payment_status)
    order.delivery_status = data.get("delivery_status", order.delivery_status)
    order.notes = data.get("notes", order.notes)
    
    order.order_updated()
    db.session.commit()

    # Automatically sets order status to complete or incomplete for testing.
    if order.payment_status == "Complete" and order.delivery_status == "Picked Up":
        order.order_status = "Complete"
    else:
        order.order_status = "Incomplete"
    
    return jsonify(order.to_dict()), 200

# Delete orders based on id.
@orders.route('/<order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id, customer_id=None):
    # If sent from customer, query based on customer id instead.
    if customer_id:
        order = Orders.query.filter_by(id=order_id, customer_id=customer_id).first()
    else:
        order = Orders.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"message": "Order " + order_id + " not found."}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order " + order_id + " deleted."}), 200
