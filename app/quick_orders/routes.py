from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Users, Orders, Customers, Cookies, Cookie_Inventory, Order_Cookies, Payment_Types
import psycopg2

from .. import db, login_manager

from . import quick_orders

# ----------------------------------------- Quick Orders -----------------------------------------
def add_cookies_to_quick_order(order_id, cookie_id, desired_quantity):
    # Make sure desired cookie exists.
    cookie = Cookies.query.filter_by(id=cookie_id).first()
    if not cookie:
        return False
    
    order_cookie = Order_Cookies(order_id=order_id, cookie_id=cookie_id, quantity = desired_quantity)
    db.session.add(order_cookie)
    return True

# Add order from order page
@quick_orders.route('/', methods=['POST'])
@login_required
def add_quick_order(customer_id=None):
    # Input is a json.
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    # A valid payment type and cookie list must be given.
    if not ('payment_type_name' in data and 'cookies' in data):
        return jsonify({'status': 'error', 'message': 'Please fill out the form!'}), 400
    
    payment_type_name = data.get("payment_type_name")
    payment_type = Payment_Types.query.filter_by(payment_type_name=payment_type_name).first()
    if not payment_type:
        return jsonify({"message": "Payment type " + payment_type_name + " not found."}), 404
    
    cookies = data.get("cookies")
    if not cookies:
        return jsonify({'status': 'error', 'message': 'No cookies given!'}), 400
    
    # Create a completed order.
    order = Orders(
        user_id=current_user.id, 
        payment_type=payment_type_name,
        notes=data.get("notes", "quick order"), 
        payment_status="Complete", 
        delivery_status="Picked Up"
    )

    # Order must be committed before its id can be used to add cookies. 
    db.session.add(order)
    db.session.commit()
    
    # Add all desired cookies to quick order.
    for cookie in cookies:
        if not add_cookies_to_quick_order(order.id, cookie["id"], cookie["quantity"]):
            # If order can't be completed, delete it from database. 
            db.session.delete(order)
            db.session.commit()
            return jsonify({"message": "Cookie " + cookie["id"] + " doesn't exist."}), 404
    
    db.session.commit()
    order.order_status = "Complete"
    return jsonify(order.to_dict()), 200
    