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

# Add order from order page
@order_cookies.route('/<order_id>', methods=['POST'])
@login_required
def add_order_cookie(order_id):
    if ('cookie_id' in request.form):
        cookie_id = request.form.get("cookie_id")
        order = Orders.query.filter_by(id=order_id).first()
        # Make sure customer exists before making an order for them.
        if not order:
            return "I'm sorry, customer with" + order_id + " doesn't exist. Please create a customer and try again."
        
        # Make sure this entry doesn't already exist
        order_cookie = Order_Cookies.query.filter_by(order_id=order_id, cookie_id=cookie_id).first()
        if order_cookie:
            return "I'm sorry, this entry already exists. :("
    

        order_cookie = Order_Cookies(order_id=order_id, cookie_id=cookie_id)
        db.session.add(order_cookie)
        db.session.commit()
        return order_cookie.to_dict()
    return "Please fill out the form!"

# Show orders based on id.
@order_cookies.route('/<order_id>/<cookie_id>', methods=['GET'])
@login_required
def read_order_cookie(order_id, cookie_id):
    order_cookie = Order_Cookies.query.filter_by(order_id=order_id, cookie_id=cookie_id).first()
    if not order_cookie:
        return "I'm sorry, you don't this order. :("
    return order_cookie.to_dict()

# Delete orders based on id.
@order_cookies.route('/<order_id>/<cookie_id>', methods=['DELETE'])
@login_required
def delete_order_cookie(order_id, cookie_id):
    # If sent from customer, query based on customer id instead.
    order_cookie = Order_Cookies.query.filter_by(order_id=order_id, cookie_id=cookie_id).first()
    if not order_cookie:
        return "I'm sorry, you don't this order. :("
    db.session.delete(order_cookie)
    db.session.commit()
    return "Entry deleted! :D"
