from flask import request, jsonify
from flask_login import current_user, login_user, login_required, logout_user
from flask_cors import CORS

from ..models import Users
import psycopg2

from .. import db

from . import auth


# ----------------------------------------- Auth -----------------------------------------
@auth.route('/register', methods=['GET','POST'])
def register():
    if (request.method == 'POST' 
        and 'email' in request.form 
        and 'password' in request.form 
        and 'password_confirm' in request.form
        and 'first_name' in request.form
        and 'last_name' in request.form):

        # Retreive and validate email
        email = request.form.get("email").strip().lower()
        
        if Users.query.filter_by(email=email).first():
            return "Account with this email already exists!"
        
        new_user = Users(first_name=request.form.get("first_name").strip().capitalize(), last_name=request.form.get("last_name").strip().capitalize())

        # Validate and set email
        email_flag = new_user.set_email(email)
        if email_flag: 
            return email_flag
        
        # Retrieve and validate password
        password_flag = new_user.set_password(
            request.form.get("password"), 
            request.form.get("password_confirm"))
        if password_flag: 
            return password_flag
        
        db.session.add(new_user)
        db.session.commit()

        # Initialize all cookie inventories to 0.
        new_user.update_cookie_inventory()
        return "New user added"
        # return redirect(url_for('login'))
    elif request.method == 'POST':
        return "Please fill out the form!"
    return "What you getting at?"

@auth.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({'status': 'error', 'message': 'You are already logged in!'}), 400
    if 'email' in request.form and 'password' in request.form:
        email = request.form.get("email")
        password = request.form.get("password")
        user = Users.query.filter_by(email=email).first()
        
        # Validate user existence and that password matches
        if user is None: 
            return jsonify({'status': 'error', 'message': 'Account with this email doesn\'t exist.'}), 400
        elif not user.check_password(password):
            return jsonify({'status': 'error', 'message': 'Password is incorrect.'}), 400
        else:
            login_user(user)
            # Update their cookies.
            user.update_cookie_inventory()
            return jsonify({'status': 'success', 'message': 'Welcome back!'}), 200
    return jsonify({'status': 'error', 'message': 'Please fill out the form!'}), 400

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return "Logged Out", 200

# Delete users based on id.
@auth.route('/delete_account', methods=['DELETE'])
@login_required
def delete_user():
    if ('password' in request.form):
        # Retreive and verify password
        password = request.form.get("password")
        if not password: 
            return "Please enter current password to confirm change."
        if not current_user.check_password(password):
            return "Password is incorrect. Please try again."
        user = Users.query.get(current_user.id)
        if user:
            db.session.delete(user)
            db.session.commit()
            logout_user
            return "Your account has been deleted! :D"
        return jsonify({'status': 'error', 'message': 'An account with this id has not been found.'}), 400
        
    return jsonify({'status': 'error', 'message': 'Please fill out the form!'}), 400