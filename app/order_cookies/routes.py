from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Users, Orders, Customers, Cookies, Cookie_Inventory, Order_Cookies
import psycopg2

from .. import db, login_manager

from . import order_cookies

# ----------------------------------------- Cookie Order_Cookies -----------------------------------------

# Show order cookie
@order_cookies.route('/<order_id>/<cookie_id>', methods=['GET'])
@login_required
def read_order_cookie(order_id, cookie_id):
    order_cookie = Order_Cookies.query.filter_by(order_id=order_id, cookie_id=cookie_id).first()
    if not order_cookie:
        return jsonify({"message": "Cookie " + cookie_id + " for order " + order_id + " not found."}), 404
    return jsonify(order_cookie.to_dict()), 200

# Add cookie to order
@order_cookies.route('/<order_id>/<cookie_id>', methods=['POST'])
@login_required
def add_order_cookie(order_id, cookie_id):
    # 0 desired if none given.
    desired_quantity = int(request.form.get("quantity", 0))
    # Make sure order exists.
    order = Orders.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"message": "Order " + order_id + " not found."}), 404
    
    # Make sure desired cookie exists and that enough exists in inventory.
    cookie_inventory = Cookie_Inventory.query.filter_by(user_id=current_user.id, cookie_id=cookie_id).first()
    if not cookie_inventory:
        return jsonify({"message": "You do not have any of cookie " + cookie_id + "."}), 404
    if cookie_inventory.projected_inventory < desired_quantity:
        return jsonify({"message": "Your order wants "+ desired_quantity + " of cookie " + cookie_id + ", but you only have " + cookie_inventory.projected_inventory + "."}), 402
    
    # Make sure this entry doesn't already exist
    order_cookie = Order_Cookies.query.filter_by(order_id=order_id, cookie_id=cookie_id).first()
    if order_cookie:
        return jsonify({"message": "Cookie " + cookie_id + " for order " + order_id + " already exists."}), 404

    order_cookie = Order_Cookies(order_id=order_id, cookie_id=cookie_id, quantity = desired_quantity)
    db.session.add(order_cookie)
    
    # Check for updates
    order.payment_status_check()
    order.order_updated()
    db.session.commit()
    return jsonify(order_cookie.to_dict()), 200

# Patch an order's cookie
@order_cookies.route('/<order_id>/<cookie_id>', methods=['PATCH'])
@login_required
def patch_order_cookie(order_id, cookie_id):
    # Make sure this entry exists.
    order_cookie = Order_Cookies.query.filter_by(order_id=order_id, cookie_id=cookie_id).first()
    if not order_cookie:
        return jsonify({"message": "Cookie " + cookie_id + " for order " + order_id + " not found."}), 404
    
    desired_quantity = int(request.form.get("quantity", order_cookie.quantity))

    # Make sure desired cookie exists and that enough exists in inventory.
    cookie_inventory = Cookie_Inventory.query.filter_by(user_id=current_user.id, cookie_id=cookie_id).first()
    if not cookie_inventory:
        return jsonify({"message": "You do not have any of cookie " + cookie_id + "."}), 404
    # Remember that the projected inventory also includes the current order, so adjust calculation for that. 
    if (cookie_inventory.projected_inventory + order_cookie.quantity) < desired_quantity:
        return jsonify({"message": "Your order wants "+ (desired_quantity - order_cookie.quantity) + " more of cookie " + cookie_id + ", but you only have " + cookie_inventory.projected_inventory + "."}), 402
    
    # Check for updates
    order_cookie.orders.payment_status_check()
    order_cookie.orders.order_updated()

    db.session.commit()
    return jsonify(order_cookie.to_dict()), 200

# Delete cookie from order based on id.
@order_cookies.route('/<order_id>/<cookie_id>', methods=['DELETE'])
@login_required
def delete_order_cookie(order_id, cookie_id):
    order = Orders.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"message": "Order " + order_id + " not found."}), 404
    
    order_cookie = Order_Cookies.query.filter_by(order_id=order_id, cookie_id=cookie_id).first()
    if not order_cookie:
        return jsonify({"message": "Cookie " + cookie_id + " for order " + order_id + " not found."}), 404
    db.session.delete(order_cookie)
    order.payment_status_check()
    order.order_updated()
    db.session.commit()
    return jsonify({"message": "Cookie " + cookie_id + " for order " + order_id + " deleted."}), 200
