
from . import db, bcrypt, login_manager
from flask_login import UserMixin
from . import user_validate

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    cookies = db.relationship('Cookie_Inventory', back_populates = 'users', cascade="all, delete-orphan")
    customers = db.relationship('Customers', back_populates = 'users', cascade="all, delete-orphan")

    def set_email(self, email):
        # Make sure that email is in a valid format.
        email, email_valid = user_validate.is_email_valid(email)
        if not email_valid: 
            return email
        self.email = email
        return None

    def set_password(self, password, password_confirm):
        # Make sure that both passwords match.
        if not user_validate.do_passwords_match(password, password_confirm):
            return "Passwords should match!"
        
        # Make sure that the password is in a valid format.
        password_flag = user_validate.is_password_valid(password)
        if password_flag: 
            return password_flag
        
        # If input password has passed all tests, set the password.
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        return None
    
    # Make sure password matches
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    # Update inventory
    def update_cookie_inventory(self):
        all_cookies = Cookies.query.all()
        existing_cookie_inventorys = {uc.cookie_id: uc for uc in self.cookies}
        
        for cookie in all_cookies:
            if cookie.id not in existing_cookie_inventorys:
                new_cookie_inventory = Cookie_Inventory(user_id=self.id, cookie_id=cookie.id, inventory=0)
                db.session.add(new_cookie_inventory)
        db.session.commit()

    # Retrieve Current User's Customers
    def retrieve_customer_list(self):
        return self.customers
    
    # Read a single customer
    def retrieve_customer(self, id):
        return Customers.query.filter_by(id=id, user_id=self.id).first()

# User loader for flask-login
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

class Cookies(db.Model):
    __tablename__ = 'cookies'
    id = db.Column(db.SmallInteger, primary_key=True)
    cookie_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String, nullable=False, default='')
    price = db.Column(db.String, nullable=False, default=0)
    picture_url = db.Column(db.String, nullable=False, default='')
    users = db.relationship('Cookie_Inventory', back_populates = 'cookies', cascade="all, delete-orphan")
    orders = db.relationship('Order_Cookies', back_populates = 'cookies', cascade="all, delete-orphan")

class Customers(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    users = db.relationship('Users', back_populates='customers')
    orders = db.relationship('Orders', back_populates='customers', cascade="all, delete-orphan")
    
    def __init__(self, first_name, last_name, user_id):
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id


class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    payment_id = db.Column(db.Integer)
    cost = db.Column(db.Integer, nullable=False, default=0)
    payment_received = db.Column(db.Integer, nullable=False, default=0)
    date_added = db.Column(db.Date, default=db.func.current_timestamp())
    
    customers = db.relationship('Customers', back_populates='orders')
    cookies = db.relationship('Order_Cookies', back_populates = 'orders', cascade="all, delete-orphan")

    def __init__(self, customer_id, payment_id):
        self.customer_id = customer_id
        self.payment_id = payment_id
        self.cost = 0

class Cookie_Inventory(db.Model):
    __tablename__ = 'cookie_inventory'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    cookie_id = db.Column(db.SmallInteger, db.ForeignKey('cookies.id'), primary_key=True)
    inventory = db.Column(db.Integer, nullable=False, default=0)
    users = db.relationship('Users', back_populates='cookies')
    cookies = db.relationship('Cookies', back_populates = 'users')

    def __init__(self, user_id, cookie_id, inventory):
        self.user_id = user_id
        self.cookie_id = cookie_id
        self.inventory = inventory

class Order_Cookies(db.Model):
    __tablename__ = 'order_cookies'
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    cookie_id = db.Column(db.Integer, db.ForeignKey('cookies.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    cost = db.Column(db.Integer, nullable=False, default=0)
    orders = db.relationship('Orders', back_populates='cookies')
    cookies = db.relationship('Cookies', back_populates = 'orders')
    
    def __init__(self, order_id, cookie_id):
        self.order_id = order_id
        self.cookie_id = cookie_id
        self.quantity = 0
        self.cost = 0

if __name__ == "__main__":
    # Run this file directly to create the database tables.
    print("Creating database tables...")
    db.create_all()
    print("Done!")