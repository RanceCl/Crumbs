from flask import request
from flask_login import current_user, login_user, login_required, logout_user
# from flask_cors import CORS

from models import Users
import user_validate
import psycopg2

from app import app, db, login_manager

# User loader for flask-login
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

# Returns content
@app.route("/")
def home():
    return "That's the way the cookie crumbles!"

@app.route('/register', methods=['GET','POST'])
def register():
    if (request.method == 'POST' 
        and 'email' in request.form 
        and 'password' in request.form 
        and 'password_confirm' in request.form):

        # Retreive and validate email
        email = request.form.get("email")
        email, email_valid = user_validate.is_email_valid(email)
        if not email_valid: 
            return email
        if Users.query.filter_by(email=email).first():
            return "Account with this email already exists!"
        
        # Retrieve and validate password
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")
        if not user_validate.do_passwords_match(password, password_confirm):
            return "Passwords should match!"
        password, password_valid = user_validate.is_password_valid(password)
        if not password_valid: 
            return password
        
        # Hash password
        new_user = Users(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return "New user added"
        # return redirect(url_for('login'))
    elif request.method == 'POST':
        return "Please fill out the form!"
    return "What you getting at?"

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return "You are already logged in!"
    if (request.method == 'POST' 
        and 'email' in request.form 
        and 'password' in request.form):
        email = request.form.get("email")
        password = request.form.get("password")
        user = Users.query.filter_by(email=email).first()
        
        # Validate user existence and that password matches
        if user is None: 
            return "Account with this email doesn't exist. Please try again."
        elif not user.check_password(password):
            return "Password is incorrect. Please try again."
        else:
            login_user(user)
            return "Welcome back!"
    elif request.method == 'POST':
        return "Please fill out the form!"
    return "What you getting at?"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return "Logged Out"

'''
@app.route('/users', methods=['POST'])
@login_required
def create():
    email = request.form.get("email")
    password = request.form.get("password")
    return db_methods.user_create(email, password)
'''

# Show account based on id.
@app.route('/users', methods=['GET'])
@login_required
def read():
    #current_user.email
    return {'id': current_user.id, 'email': current_user.email, 'password': current_user.password_hash}
    #return db_methods.user_read_by_id(id)

# Update account email.
@app.route('/users/change_email', methods=['GET','PATCH'])
@login_required
def change_email():
    if (request.method == 'PATCH' 
        and 'new_email' in request.form 
        and 'password' in request.form):

        # Retreive and verify password
        password = request.form.get("password")
        if not password: 
            return "Please enter current password to confirm change."
        if not current_user.check_password(password):
            return "Password is incorrect. Please try again."

        # Retreive and validate new email
        new_email = request.form.get("new_email")
        new_email, email_valid = user_validate.is_email_valid(new_email)
        if not email_valid: 
            return new_email
        if Users.query.filter_by(email=new_email).first():
            return "Account with this email already exists!"
        
        # Change email
        current_user.email = new_email
        db.session.commit()
        return "Email changed!"
    elif request.method == 'PATCH':
        return "Please fill out the form!"
    return "What you getting at?"

# Update account password.
@app.route('/users/change_password', methods=['GET','PATCH'])
@login_required
def change_password():
    if (request.method == 'PATCH' 
        and 'password' in request.form 
        and 'new_password' in request.form 
        and 'new_password_confirm' in request.form):

        # Retreive and verify old password
        password = request.form.get("password")
        if not password: 
            return "Please enter current password to confirm change."
        if not current_user.check_password(password):
            return "Password is incorrect. Please try again."
        
        # Retrieve and validate new password
        new_password = request.form.get("new_password")
        new_password_confirm = request.form.get("new_password_confirm")
        if not user_validate.do_passwords_match(new_password, new_password_confirm):
            return "Passwords should match!"
        new_password, password_valid = user_validate.is_password_valid(new_password)
        if not password_valid: 
            return new_password
        
        # Change password
        current_user.set_password(new_password)
        db.session.commit()
        return "Password changed!"
    elif request.method == 'PATCH':
        return "Please fill out the form!"
    return "What you getting at?"

'''
# Delete account.
@app.route('/users/<id>', methods=['DELETE'])
@login_required
def delete():
    return "User deleted!"
'''

def add_user(email, password):
    new_user = Users(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()


@app.route('/populate_users')
def populate_users():
    Users.query.delete()
    add_user("chadgregpaulthompson@gmail.com", "Ch@t3PT")
    add_user("anonymous@email.com", "S3cr3t P@$$word")
    add_user("known@email.com", "S33n P@$$word")

    return "Table populated"
    # return redirect(url_for('login'))
