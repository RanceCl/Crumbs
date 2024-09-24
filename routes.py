from flask import request, jsonify
from flask_login import current_user, login_user, login_required, logout_user
from flask_cors import CORS

from models import Users, Orders, Customers, Cookies, Cookie_Inventory, Cookie_Orders
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

# ----------------------------------------- Auth -----------------------------------------
@app.route('/register', methods=['GET','POST'])
def register():
    if (request.method == 'POST' 
        and 'email' in request.form 
        and 'password' in request.form 
        and 'password_confirm' in request.form
        and 'first_name' in request.form
        and 'last_name' in request.form):

        # Retreive and validate email
        email = request.form.get("email")
        
        if Users.query.filter_by(email=email).first():
            return "Account with this email already exists!"
        
        new_user = Users(first_name=request.form.get("first_name"),
                         last_name=request.form.get("last_name"))
        

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

@app.route('/login', methods=['POST'])
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
            # user.update_cookie_inventory()
            return jsonify({'status': 'success', 'message': 'Welcome back!'}), 200
    return jsonify({'status': 'error', 'message': 'Please fill out the form!'}), 400

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return "Logged Out", 200

'''
@app.route('/users', methods=['POST'])
@login_required
def create():
    email = request.form.get("email")
    password = request.form.get("password")
    return db_methods.user_create(email, password)
'''
# ----------------------------------------- COOKIES -----------------------------------------
#Get all of the cookies
@app.route('/cookies', methods=['GET'])
def get_all_cookies():
    cookies = Cookies.query.all()
    if not cookies:
        return {"message": "No cookies found."}, 404

    cookies_list = [
        {
            'id': cookie.id,
            'name': cookie.cookie_name,
            'price': cookie.price,
            'description': cookie.description,
            'picture': cookie.picture_url
        }
        for cookie in cookies
    ]
    return {'cookies': cookies_list}, 200

# Show single cookie information
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

# ----------------------------------------- Inventory -----------------------------------------
# Retrieve inventory
@app.route('/users/inventory', methods=['GET'])
@login_required
def get_user_inventory():
    inventory = db.session.query(Cookies.cookie_name, Cookie_Inventory.inventory).join(Cookie_Inventory).filter(Cookie_Inventory.user_id == current_user.id).all()
    # inventory = Cookies.query.join(Cookie_Inventory).filter(Cookie_Inventory.user_id == current_user.id).all()
    return {cookie_name: count for cookie_name, count in inventory}

# Edit inventory
@app.route('/users/inventory', methods=['POST', 'PATCH'])
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
@app.route('/users/inventory', methods=['DELETE'])
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



# ----------------------------------------- Customers -----------------------------------------
# Retrieve customers
@app.route('/customers', methods=['GET'])
@login_required
def get_customer_list():
    # User.query.join(Skill).filter(Skill.skill == skill_name).all()
    customers = Customers.query.filter_by(user_id=current_user.id).all()
    result = []
    for customer in customers:
        result.append({
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            'user_id': customer.user_id
        })
    return {"customers": result}, 200

# Create customer
@app.route('/customers', methods=['POST'])
@login_required
def add_customer():
    if ('first_name' in request.form
        and 'last_name' in request.form):
        first_name=request.form.get("first_name")
        last_name=request.form.get("last_name")
        new_customer = Customers(first_name=first_name,
                                 last_name=last_name,
                                 user_id=current_user.id)
        db.session.add(new_customer)
        db.session.commit()

        return first_name + " " + last_name + " added as a customer!"
    return "Please fill out the form!"

# Show customers based on id.
@app.route('/customers/<id>', methods=['GET'])
@login_required
def read_customer(id):
    customer = Customers.query.filter_by(id=id, user_id=current_user.id).first()
    if not customer:
        return "I'm sorry, " + id + " doesn't exist. :("
    return {'id': customer.id, 
            'first_name': customer.first_name, 
            'last_name': customer.last_name, 
            'user_id': customer.user_id}

# Update customers based on id.
@app.route('/customers/<id>', methods=['PATCH'])
@login_required
def update_customer(id):
    if ('first_name' in request.form
        and 'last_name' in request.form):
        customer = Customers.query.filter_by(id=id, user_id=current_user.id).first()
        if not customer:
            return "I'm sorry, " + id + " doesn't exist. :("
        customer.first_name =request.form.get("first_name")
        customer.last_name =request.form.get("last_name")
        db.session.commit()
        return {'id': customer.id, 
                'first_name': customer.first_name, 
                'last_name': customer.last_name, 
                'user_id': customer.user_id}
    return "Please fill out the form!"

# Delete customers based on id.
@app.route('/customers/<id>', methods=['DELETE'])
@login_required
def delete_customer(id):
    Customers.query.filter_by(id=id, user_id=current_user.id).delete()
    db.session.commit()
    return id + " deleted! :D"


# ----------------------------------------- User Info -----------------------------------------
# Show account based on id.
@app.route('/users', methods=['GET'])
@login_required
def read():
    #current_user.email
    return {'id': current_user.id, 
            'email': current_user.email, 
            'password': current_user.password_hash}
    #return db_methods.user_read_by_id(id)

#Use Flask-Login to get current user
@app.route('/current-user', methods=['GET'])
@login_required
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            'id': current_user.id,
            'email': current_user.email,
        }), 200
    return jsonify({'error': 'User not authenticated'}), 401    

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
# ----------------------------------------- Dev Tests -----------------------------------------
def add_user(email, password, first_name, last_name):
    password_confirm = password
    new_user = Users(email=email, first_name=first_name, last_name=last_name)
    if not new_user.set_password(password, password_confirm):
        db.session.add(new_user)
        db.session.commit()
    return None

def add_customer(first_name, user_id):
    new_customer = Customers(first_name=first_name,
                            last_name=first_name,
                            user_id=user_id)
    #current_user.append(new_customer)
    db.session.add(new_customer)
    db.session.commit()
    return None

@app.route('/populate_users', methods=['GET','POST'])
def populate_users():
    Users.query.delete()
    add_user("chadgregpaulthompson@gmail.com", "Ch@t3PT", "Chad", "GPT")
    add_user("anonymous@email.com", "S3cr3t P@$$word", "Anonymous", "NoLastName")
    add_user("known@email.com", "S33n P@$$word", "Known", "HasLastName")
    add_user("elmo@email.com", "B33G B1rd$", "Elmo", "Sesame")
    

    return "Table populated"
    # return redirect(url_for('login'))

@app.route('/populate_customers', methods=['GET','POST'])
def populate_customers():
    Customers.query.delete()
    add_customer("Chad", 1)
    add_customer("Jim", 2)
    add_customer("Known", 3)
    add_customer("Jane", 4)
    add_customer("Don", 1)
    add_customer("Abe", 2)
    add_customer("Corey", 3)
    add_customer("Linda", 4)
    add_customer("Leen", 1)
    add_customer("Noni", 2)
    add_customer("Chi-Chi", 3)
    add_customer("Best", 4)
    add_customer("Midnight", 1)
    add_customer("Marley", 2)
    add_customer("Known", 3)
    add_customer("Chad", 4)

    return "Customers populated"
