from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Users, Orders, Customers, Cookies, Cookie_Inventory, Order_Cookies
import psycopg2

from .. import db, login_manager

from . import users


# ----------------------------------------- User Info -----------------------------------------
# Show account based on id.
@users.route('/', methods=['GET'])
@login_required
def read():
    #current_user.email
    return current_user.to_dict()
    #return db_methods.user_read_by_id(id)

# Update account email.
@users.route('/change_email', methods=['GET','PATCH'])
@login_required
def change_email():
    # Input is a json.
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    if (request.method == 'PATCH' 
        and 'new_email' in data 
        and 'password' in data):

        # Retreive and verify password
        password = data.get("password")
        if not password: 
            return "Please enter current password to confirm change."
        if not current_user.check_password(password):
            return "Password is incorrect. Please try again."

        # Retreive and validate new email
        new_email = data.get("new_email")
        if Users.query.filter_by(email=new_email).first():
            return "Account with this email already exists!"
        
        email_flag = current_user.set_email(new_email)
        if email_flag: 
            return email_flag
        
        # Change email
        current_user.email = new_email
        db.session.commit()
        return "Email changed!"
    elif request.method == 'PATCH':
        return "Please fill out the form!"
    return "What you getting at?"

# Update account password.
@users.route('/change_password', methods=['GET','PATCH'])
@login_required
def change_password():
    # Input is a json.
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid request"}), 400
    
    if (request.method == 'PATCH' 
        and 'password' in data 
        and 'new_password' in data 
        and 'new_password_confirm' in data):

        # Retreive and verify old password
        password = data.get("password")
        if not password: 
            return "Please enter current password to confirm change."
        if not current_user.check_password(password):
            return "Password is incorrect. Please try again."
        
        # Retrieve and validate new password
        new_password = data.get("new_password")
        new_password_confirm = data.get("new_password_confirm")

        password_flag = current_user.set_password(new_password, new_password_confirm)
        if password_flag: 
            return password_flag
        
        db.session.commit()
        return "Password changed!"
    elif request.method == 'PATCH':
        return "Please fill out the form!"
    return "What you getting at?"
