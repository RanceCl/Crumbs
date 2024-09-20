from flask import request, jsonify
from flask_login import current_user, login_user, login_required, logout_user
from flask_cors import CORS

from models import Users, Cookies, Cookie_Inventory
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
        
        if Users.query.filter_by(email=email).first():
            return "Account with this email already exists!"
        
        new_user = Users()

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
            # Update their cookies.
            # user.update_cookie_inventory()
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

# Show cookie information
@app.route('/cookie/<cookie_name>', methods=['GET'])
def cookie_read(cookie_name):
    cookie = Cookies.query.filter_by(cookie_name=cookie_name).first()
    if not cookie:
        return "I'm sorry, " + cookie_name + " doesn't exist. :("
    return {'id': cookie.id, 
            'name': cookie.cookie_name, 
            'price': cookie.price, 
            'description': cookie.description, 
            'picture': cookie.picture_url}

# Retrieve inventory
@app.route('/users/inventory', methods=['GET'])
@login_required
def get_user_inventory():
    inventory = db.session.query(Cookies.cookie_name, Cookie_Inventory.inventory).join(Cookie_Inventory).filter(Cookie_Inventory.user_id == current_user.id).all()
    # inventory = Cookies.query.join(Cookie_Inventory).filter(Cookie_Inventory.user_id == current_user.id).all()
    return {cookie_name: count for cookie_name, count in inventory}

# Edit inventory
@app.route('/users/inventory', methods=['POST'])
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
            db.session.commit()
            return cookie_name + " added to inventory table! You have " + inventory + " in stock! :D"
        cookie_inventory.inventory = inventory
        db.session.commit()
        return cookie_name + " inventory updated! You have " + inventory + " in stock! :D"
    return "Please fill out the form!"


# Show account based on id.
@app.route('/users', methods=['GET'])
@login_required
def read():
    #current_user.email
    return {'id': current_user.id, 
            'email': current_user.email, 
            'password': current_user.password_hash}
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

        password_flag = current_user.set_password(new_password, new_password_confirm)
        if password_flag: 
            return password_flag
        
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
    password_confirm = password
    new_user = Users(email=email)
    if not new_user.set_password(password, password_confirm):
        db.session.add(new_user)
        db.session.commit()


@app.route('/populate_users', methods=['GET','POST'])
def populate_users():
    Users.query.delete()
    add_user("chadgregpaulthompson@gmail.com", "Ch@t3PT")
    add_user("anonymous@email.com", "S3cr3t P@$$word")
    add_user("known@email.com", "S33n P@$$word")

    return "Table populated"
    # return redirect(url_for('login'))
