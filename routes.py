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

# Delete users based on id.
@app.route('/delete_account', methods=['DELETE'])
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
        return "I'm sorry, a customer " + id + " doesn't belong to you. :("
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
            return "I'm sorry, a customer " + id + " doesn't belong to you. :("
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


# Show customer orders based on id.
@app.route('/customers/<id>/orders', methods=['GET'])
@login_required
def read_customer_orders(id):
    #orders = Orders.query.join(Customers).filter(Customers.user_id==current_user.id, Orders.id==id).first()
    orders = Orders.query.join(Customers).filter_by(id=id).all()
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "customer_id": order.customer_id,
            "customer_first_name": order.customers.first_name,
            "customer_last_name": order.customers.last_name,
            'user_id': order.customers.user_id,
            'payment_id': order.payment_id
        })
    return {"orders": result}, 200

# Add order to customer
@app.route('/customers/<id>/orders', methods=['POST', 'PATCH'])
@login_required
def add_customer_order(id):
    if ('payment_id' in request.form):
        payment_id = request.form.get("payment_id")
        order = Orders(customer_id=id,payment_id=payment_id)
        db.session.add(order)
        db.session.commit()
        return {'id': order.id, 
                'customer': order.customer_id, 
                'payment': order.payment_id, 
                'cost': order.cost}
    return "Please fill out the form!"

# Show customer order based on id.
@app.route('/customers/<id>/orders/<order_id>', methods=['GET'])
@login_required
def read_customer_order(id, order_id):
    order = Orders.query.join(Customers).filter(Customers.id==id, Orders.id==order_id).first()
    if not order:
        return "I'm sorry, customer " + id + " doesn't have an order with id " + order_id + ". :("
    return {'id': order.id, 
            'customer': order.customer_id, 
            'payment': order.payment_id, 
            'cost': order.cost}

# Update customer orders based on id.
@app.route('/customers/<id>/orders/<order_id>', methods=['PATCH'])
@login_required
def update_customer_order(id, order_id):
    if ('payment_id' in request.form):
        order = Orders.query.join(Customers).filter(Customers.id==id, Orders.id==order_id).first()
        if not order:
            return "I'm sorry, customer " + id + " doesn't have an order with id " + order_id + ". :("
        order.payment_id = request.form.get("payment_id")
        db.session.commit()
        return {'id': order.id, 
                'customer': order.customer_id, 
                'payment': order.payment_id, 
                'cost': order.cost}
    return "Please fill out the form!"

# Delete customer orders based on id.
@app.route('/customers/<id>/orders/<order_id>', methods=['DELETE'])
@login_required
def delete_customer_order(id, order_id):
    Orders.query.filter_by(id=order_id).delete()
    db.session.commit()
    return order_id + " deleted! :D"

# ----------------------------------------- Orders -----------------------------------------
# Retrieve orders 
@app.route('/orders', methods=['GET'])
@login_required
def get_orders_list():
    # inventory = db.session.query(Cookies.cookie_name, Cookie_Inventory.inventory).join(Customers).filter(Customers.user_id == current_user.id).all()
    # inventory = db.session.query(Cookies.cookie_name, Cookie_Inventory.inventory).join(Cookie_Inventory).filter(Cookie_Inventory.user_id == current_user.id).all()
    
    orders = Orders.query.join(Customers).filter_by(user_id=current_user.id).all()
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "customer_id": order.customer_id,
            "customer_first_name": order.customers.first_name,
            "customer_last_name": order.customers.last_name,
            'user_id': order.customers.user_id,
            'payment_id': order.payment_id
        })
    return {"orders": result}, 200

# Add order from order page
@app.route('/orders', methods=['POST', 'PATCH'])
@login_required
def add_order():
    if ('customer_id' in request.form
        and 'payment_id' in request.form):
        customer_id = request.form.get("customer_id")
        payment_id = request.form.get("payment_id")
        customer = Customers.query.filter_by(id=id).first()
        # Make sure customer exists before making an order for them.
        if not customer:
            return "I'm sorry, customer with" + id + " doesn't exist. Please create a customer and try again."
        
        order = Orders(customer_id=customer_id,payment_id=payment_id)
        db.session.add(order)
        db.session.commit()
        return {'id': order.id, 
                'customer': order.customer_id, 
                'payment': order.payment_id, 
                'cost': order.cost}
    return "Please fill out the form!"

# Show orders based on id.
@app.route('/orders/<id>', methods=['GET'])
@login_required
def read_order(id):
    order = Orders.query.join(Customers).filter(Orders.id==id).first()
    if not order:
        return "I'm sorry, you don't have an order with id " + id + ". :("
    return {'id': order.id, 
            'customer': order.customer_id, 
            'payment': order.payment_id, 
            'cost': order.cost}

# Update orders based on id.
@app.route('/orders/<id>', methods=['PATCH'])
@login_required
def update_order(id):
    if ('customer_id' in request.form
        and 'payment_id' in request.form):
        order = Orders.query.join(Customers).filter(Orders.id==id).first()
        if not order:
            return "I'm sorry, you don't have an order with id " + id + ". :("
        order.customer_id = request.form.get("customer_id")
        order.payment_id = request.form.get("payment_id")
        db.session.commit()
        return {'id': order.id, 
                'customer': order.customer_id, 
                'payment': order.payment_id, 
                'cost': order.cost}
    return "Please fill out the form!"

# Delete orders based on id.
@app.route('/orders/<id>', methods=['DELETE'])
@login_required
def delete_order(id):
    Orders.query.filter_by(id=id).delete()
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
            'first_name': current_user.first_name,
            'last_name': current_user.last_name
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


# ----------------------------------------- Dev Tests -----------------------------------------
def add_user(email, password, first_name, last_name):
    password_confirm = password
    new_user = Users(email=email, 
                     first_name=first_name, 
                     last_name=last_name)
    if not new_user.set_password(password, password_confirm):
        db.session.add(new_user)
        db.session.commit()
    return None

def add_order(customer_id, payment_id):
    new_order = Orders(customer_id=customer_id,
                       payment_id=payment_id)
    db.session.add(new_order)
    db.session.commit()
    return new_order.id

def add_customer(first_name, user_id):
    new_customer = Customers(first_name=first_name,
                            last_name=first_name,
                            user_id=user_id)
    #current_user.append(new_customer)
    db.session.add(new_customer)
    db.session.commit()
    return new_customer.id

@app.route('/populate_users', methods=['GET','POST'])
def populate_users():
    add_user("chadgregpaulthompson@gmail.com", "Ch@t3PT", "Chad", "GPT")
    add_user("anonymous@email.com", "S3cr3t P@$$word", "Anonymous", "NoLastName")
    add_user("known@email.com", "S33n P@$$word", "Known", "HasLastName")
    add_user("elmo@email.com", "B33G B1rd$", "Elmo", "Sesame")
    

    return "Table populated"
    # return redirect(url_for('login'))

# For each customer, add four orders
def populate_orders(customer_id):
    for _ in range(4):
        add_order(customer_id, 0)
    return None

@app.route('/populate_customers', methods=['GET','POST'])
def populate_customers():
    names = ["Chad","Jim","Known","Jane","Don","Abe","Corey","Linda","Leen","Noni","Chi-Chi","Best","Midnight","Marley","Known","Chad"]
    name_index = 0
    user_ids = [id[0] for id in Users.query.with_entities(Users.id).all()]
    for user_id in user_ids:
        # Add three names to the current user.
        for _ in range(3):
            if name_index >= len(names):
                # Stop adding customers if we've used all of the names.
                return "Customers populated"
            
            new_customer_id = add_customer(names[name_index], user_id)
            populate_orders(new_customer_id)
            name_index += 1
            
    return "Customers populated"