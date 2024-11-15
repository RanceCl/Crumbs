from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Cookies, Cookie_Inventory
import psycopg2

from .. import db, login_manager

from . import inventory


# ----------------------------------------- Inventory -----------------------------------------
# Retrieve inventory
@inventory.route('/', methods=['GET'])
@login_required
def get_user_inventory():
    cookie_inventory = Cookie_Inventory.query.join(Cookies).filter(Cookie_Inventory.user_id == current_user.id).all()
    result = {}
    for inventory in cookie_inventory:
        result[inventory.cookies.cookie_name] = {
            "inventory": inventory.inventory,
            "projected_inventory": inventory.projected_inventory,
            "description": inventory.cookies.description,
            "picture_url": inventory.cookies.picture_url}
        
    return result

# Edit inventory
@inventory.route('/', methods=['POST', 'PATCH'])
@login_required
def set_user_inventory():
    # You can only add or edit the inventory if the name and the new inventory value are provided.
    if ('cookie_name' in request.form
        and 'inventory' in request.form):
        cookie_name = request.form.get("cookie_name")
        inventory = request.form.get("inventory")
        cookie = Cookies.query.filter_by(cookie_name=cookie_name).first()
        
        # Ensure that the cookie exists.
        if not cookie:
            return jsonify({"message": "Cookie " + cookie_name + " not found."}), 404
        
        cookie_inventory = Cookie_Inventory.query.filter_by(user_id=current_user.id, cookie_id=cookie.id).first()
        # If the cookie exists, but no count does, then add it to the table.
        if not cookie_inventory: 
            cookie_inventory = Cookie_Inventory(user_id=current_user.id, cookie_id=cookie.id, inventory=inventory)
            db.session.add(cookie_inventory)
            db.session.commit()
            return jsonify({"message": cookie_name + " added to inventory table! You have " + str(inventory) + " in stock! :D"}), 200
        cookie_inventory.inventory = inventory
        # if not cookie_inventory: 
        #     cookie_inventory = Cookie_Inventory(user_id=current_user.id, cookie_id=cookie.id, inventory=inventory)
        #     cookie_inventory.update_projected_inventory()
        #     db.session.add(cookie_inventory)
        # else:
        #     # Update existing inventory and recalculate projected inventory
        #     cookie_inventory.inventory = inventory
        #     cookie_inventory.update_projected_inventory()
        db.session.commit()
        return jsonify({"message": cookie_name + " inventory updated! You have " + str(cookie_inventory.projected_inventory) + " out of " + str(inventory) + " in stock! :D"}), 200
    return jsonify({"status": "error", "message": "Please fill out the form!"}), 400

# Delete inventory
@inventory.route('/', methods=['DELETE'])
@login_required
def delete_user_inventory():
    if ('cookie_name' in request.form):
        cookie_name = request.form.get("cookie_name")
        
        cookie = Cookies.query.filter_by(cookie_name=cookie_name).first()
        
        # Ensure that the cookie exists.
        if not cookie:
            return jsonify({"message": "Cookie " + cookie_name + " not found."}), 404
        
        Cookie_Inventory.query.filter_by(user_id=current_user.id, cookie_id=cookie.id).delete()
        db.session.commit()
        return jsonify({"message": cookie_name + " inventory deleted."}), 200
    return jsonify({"status": "error", "message": "Please fill out the form!"}), 400
