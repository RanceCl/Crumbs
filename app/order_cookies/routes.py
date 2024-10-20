from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Users, Orders, Customers, Cookies, Cookie_Inventory, Order_Cookies
import psycopg2

from .. import db, login_manager

from . import order_cookies

# ----------------------------------------- Cookie Order_Cookies -----------------------------------------
# Retrieve order entries belonging to user. 
@order_cookies.route('/', methods=['GET'])
@login_required
def get_user_order_cookies_list():
    order_cookies = Order_Cookies.query.join(Orders).join(Customers).filter_by(user_id=current_user.id).all()
    result = []
    for order_cookie in order_cookies:
        result.append(order_cookie.to_dict())
    return {"order_cookies": result}, 200

# Retrieve orders 
@order_cookies.route('/<order_id>', methods=['GET'])
@login_required
def get_order_cookies_list(order_id):
    order_cookies = Order_Cookies.query.filter_by(order_id=order_id).all()
    result = []
    for order_cookie in order_cookies:
        result.append(order_cookie.to_dict())
    return {"order_cookies": result}, 200

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
    # Make sure order exists.
    order = Orders.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"message": "Order " + order_id + " not found."}), 404
    
    # Make sure desired cookie exists.
    cookie = Cookies.query.filter_by(id=cookie_id).first()
    if not cookie:
        return jsonify({"message": "Cookie " + cookie_id + " not found."}), 404
    
    # Make sure this entry doesn't already exist
    order_cookie = Order_Cookies.query.filter_by(order_id=order_id, cookie_id=cookie_id).first()
    if order_cookie:
        return jsonify({"message": "Cookie " + cookie_id + " for order " + order_id + " not found."}), 404

    order_cookie = Order_Cookies(order_id=order_id, cookie_id=cookie_id, quantity = request.form.get("quantity", 0))
    db.session.add(order_cookie)
    
    # Check for updates
    order.status = order.status
    order.order_updated()
    db.session.commit()
    return jsonify(order_cookie.to_dict()), 200

# Patch an order's cookie
@order_cookies.route('/<order_id>/<cookie_id>', methods=['PATCH'])
@login_required
def patch_order_cookie(order_id, cookie_id):
    # Make sure this entry doesn't already exist
    order_cookie = Order_Cookies.query.filter_by(order_id=order_id, cookie_id=cookie_id).first()
    if not order_cookie:
        return jsonify({"message": "Cookie " + cookie_id + " for order " + order_id + " not found."}), 404

    order_cookie.quantity = int(request.form.get("quantity", order_cookie.quantity))

    # Check for updates
    order_cookie.orders.status = order_cookie.orders.status
    order_cookie.orders.order_updated()

    db.session.commit()
    return jsonify(order_cookie.to_dict()), 200

# Delete orders based on id.
@order_cookies.route('/<order_id>/<cookie_id>', methods=['DELETE'])
@login_required
def delete_order_cookie(order_id, cookie_id):
    # If sent from customer, query based on customer id instead.
    order_cookie = Order_Cookies.query.filter_by(order_id=order_id, cookie_id=cookie_id).first()
    if not order_cookie:
        return jsonify({"message": "Cookie " + cookie_id + " for order " + order_id + " not found."}), 404
    db.session.delete(order_cookie)
    db.session.commit()
    return jsonify({"Cookie " + cookie_id + " for order " + order_id + " deleted."}), 200
