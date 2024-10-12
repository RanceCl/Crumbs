from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Users, Orders, Customers, Cookies, Cookie_Inventory, Order_Cookies
import psycopg2

from .. import db, login_manager

from . import inventory


# ----------------------------------------- Inventory -----------------------------------------
# Retrieve inventory
@inventory.route('/', methods=['GET'])
@login_required
def get_user_inventory():
    inventory = db.session.query(Cookies.cookie_name, Cookie_Inventory.inventory).join(Cookie_Inventory).filter(Cookie_Inventory.user_id == current_user.id).all()
    # inventory = Cookies.query.join(Cookie_Inventory).filter(Cookie_Inventory.user_id == current_user.id).all()
    return {cookie_name: count for cookie_name, count in inventory}

# Edit inventory
@inventory.route('/', methods=['POST', 'PATCH'])
@login_required
def set_user_inventory():
    if ('cookie_name' in request.form
        and 'inventory' in request.form):
        cookie_name = request.form.get("cookie_name")
        inventory=request.form.get("inventory")

        cookie = Cookies.query.filter_by(cookie_name=cookie_name).first()
        
        # Ensure that the cookie exists.
        if not cookie:
            return "I'm sorry, " + cookie_name + " doesn't exist. :("
        
        cookie_inventory = Cookie_Inventory.query.filter_by(user_id=current_user.id, cookie_id=cookie.id).first()
        # If the cookie exists, but no count does, then add it to the table.
        if not cookie_inventory: 
            cookie_inventory = Cookie_Inventory(
                user_id=current_user.id, 
                cookie_id=cookie.id, 
                inventory=inventory)
            db.session.add(cookie_inventory)
            db.session.commit()
            return cookie_name + " added to inventory table! You have " + inventory + " in stock! :D"
        cookie_inventory.inventory = inventory
        db.session.commit()
        return cookie_name + " inventory updated! You have " + inventory + " in stock! :D"
    return "Please fill out the form!"

# Delete inventory
@inventory.route('/', methods=['DELETE'])
@login_required
def delete_user_inventory():
    if ('cookie_name' in request.form):
        cookie_name = request.form.get("cookie_name")
        
        cookie = Cookies.query.filter_by(cookie_name=cookie_name).first()
        
        # Ensure that the cookie exists.
        if not cookie:
            return "I'm sorry, " + cookie_name + " doesn't exist. :("
        
        Cookie_Inventory.query.filter_by(user_id=current_user.id, cookie_id=cookie.id).delete()
        db.session.commit()
        return cookie_name + " deleted! :D"
    return "Please fill out the form!"
