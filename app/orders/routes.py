from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Users, OrderStatus, PaymentStatus, DeliveryStatus, Orders, Customers, Cookies, Cookie_Inventory, Order_Cookies
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
            return jsonify({"message": "Customer " + customer_id + " not found."}), 404
        
        order = Orders(
            customer_id=customer_id,
            payment_id=payment_id,
            notes=request.form.get("notes", "")
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
    order.payment_id = request.form.get("payment_id", order.payment_id)
    order.order_status = request.form.get("order_status", order.order_status)
    order.notes = request.form.get("notes", order.notes)
    
    order.payment_status_check()
    # Only add funds when payment type is confirmed.
    if (order.payment_status != PaymentStatus.PAYMENT_INVALID) and (order.payment_status != PaymentStatus.PAYMENT_UNCONFIRMED):
        order.payment_received += float(request.form.get("payment_received", 0))
        # Check after funds are added.
        order.payment_status_check()
    order.delivery_status = request.form.get("delivery_status", order.delivery_status)

    order.order_updated()
    db.session.commit()
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
