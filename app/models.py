from enum import IntEnum
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

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
        }

# User loader for flask-login
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

class Cookies(db.Model):
    __tablename__ = 'cookies'
    id = db.Column(db.SmallInteger, primary_key=True)
    cookie_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String, nullable=False, default='')
    price = db.Column(db.Float, nullable=False, default=0)
    picture_url = db.Column(db.String, nullable=False, default='')

    users = db.relationship('Cookie_Inventory', back_populates = 'cookies', cascade="all, delete-orphan")
    orders = db.relationship('Order_Cookies', back_populates = 'cookies', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'cookie_name': self.cookie_name,
            'description': self.description,
            'price': self.price,
            'picture_url': self.picture_url
        }

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
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name
        }

class OrderStatus(IntEnum):
    UNFINISHED = 0
    FINISHED = 1

    def __str__(self):
        StatusNames={
            self.UNFINISHED : "Order isn't finished.",
            self.FINISHED : "Order is finished."
        }
        return StatusNames[self.value]
    
class PaymentStatus(IntEnum):
    PAYMENT_UNCONFIRMED = 0
    PAYMENT_COMPLETE = 1
    PAYMENT_INCOMPLETE = 2
    PAYMENT_INVALID = 3
    
    def __str__(self):
        StatusNames={
            self.PAYMENT_UNCONFIRMED : "Payment method unconfirmed.",
            self.PAYMENT_COMPLETE : "Payment has been complete. Order can now be delivered!",
            self.PAYMENT_INCOMPLETE : "Payment isn't complete.",
            self.PAYMENT_INVALID : "Payment method invalid."
        }
        return StatusNames[self.value]

class DeliveryStatus(IntEnum):
    NOT_SENT = 0
    SENT = 1
    DELIVERED = 2
    DELAYED = 3
    PICKED_UP = 4

    def __str__(self):
        StatusNames={
            self.NOT_SENT : "Order hasn't been sent.",
            self.SENT : "Order has been sent.",
            self.DELIVERED : "Order has been delivered.",
            self.DELAYED : "Order is delayed.",
            self.PICKED_UP : "Order has been picked up."
        }
        return StatusNames[self.value]


# Actual orders for the cookies.
class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    payment_id = db.Column(db.Integer)
    payment_received = db.Column(db.Float, nullable=False, default=0.00)
    date_added = db.Column(db.Date, default=db.func.current_timestamp())
    date_modified = db.Column(db.Date, default=db.func.current_timestamp())
    order_status_stored = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.UNFINISHED)
    payment_status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PAYMENT_UNCONFIRMED)
    delivery_status = db.Column(db.Enum(DeliveryStatus), nullable=False, default=DeliveryStatus.NOT_SENT)
    
    customers = db.relationship('Customers', back_populates='orders')
    cookies = db.relationship('Order_Cookies', back_populates = 'orders', cascade="all, delete-orphan")

    def __init__(self, customer_id, payment_id):
        self.customer_id = customer_id
        self.payment_id = payment_id
    
    def order_updated(self):
        self.date_modified = db.func.current_timestamp()
    
    @property
    def order_status(self):
        return self.order_status_stored
    
    @order_status.setter
    def order_status(self, new_status):
        # Order can't be complete if there are no cookies to be ordered.
        if (not self.cookies) or (new_status == OrderStatus.UNFINISHED):
            self.order_status_stored = OrderStatus.UNFINISHED
        # Otherwise, the status is decided by the user.
        else:
            self.order_status_stored = OrderStatus.FINISHED
    
    def payment_status_check(self):
        # Payment is unconfirmed if 0.
        if int(self.payment_id) == 0:
            self.payment_status = PaymentStatus.PAYMENT_UNCONFIRMED
        # Payment is invalid if it doesn't exist in the payment ID table
        # ADD LATER
        elif int(self.payment_id) == -1:
            self.payment_status = PaymentStatus.PAYMENT_INVALID
        # Payment is incomplete if the payment made hasn't exceeded the total cost.
        elif self.payment_received < self.total_cost:
            self.payment_status = PaymentStatus.PAYMENT_INCOMPLETE
        # Otherwise, the status is decided by the user.
        else:
            self.payment_status = PaymentStatus.PAYMENT_COMPLETE
    
    # Total price of the order.
    @property
    def total_cost(self):
        ret = 0.00
        for prod in self.cookies:
            ret += prod.price
        return ret
    
    def get_order_cookies(self):
        order_cookies = self.cookies
        result = []
        for order_cookie in order_cookies:
            result.append(order_cookie.to_dict())
        return result
    
    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_first_name": self.customers.first_name,
            "customer_last_name": self.customers.last_name,
            'payment_id': self.payment_id,
            'total_cost': self.total_cost,
            'payment_received': self.payment_received,
            'date_added': self.date_added,
            'date_modified': self.date_modified,
            'order_status': str(self.order_status),
            'payment_status': str(self.payment_status),
            'delivery_status': str(self.delivery_status),
            'order_cookies': self.get_order_cookies()
        }

# Each user's individual cookie count.
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
    
    # Calculate the projected inventory after the removal of all orders from the current inventory.
    @property
    def projected_inventory(self):
        # Get all of the orders associated with the user. 
        order_cookies = Order_Cookies.query.join(Orders).join(Customers).filter(Customers.user_id==self.user_id, Order_Cookies.cookie_id==self.cookie_id).all()
        resulting_quantity = self.inventory
        for order_cookie in order_cookies:
            resulting_quantity -= order_cookie.quantity
        return resulting_quantity
    '''
    # Inventory when considering orders.
    @property
    def projected_inventory(self):
        ret = self.inventory
        order_cookies = Order_Cookies.query.join(Orders).join(Customers).filter_by(user_id=self.user_id, Order_Cookies.cookie_id = ).all()
        result = []
        for order_cookie in order_cookies:
            result.append(order_cookie.to_dict())
        Order_Cookies.query.join()
        Orders.query.join(Customers).filter(Customers.id==customer_id, Orders.id==order_id).first()
        for order in self.cookies.orders:
            ret += prod.price
        return ret
    '''

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "cookie_id": self.cookie_id,
            "inventory": self.inventory,
            "projected_inventory": self.projected_inventory
        }

# Each order's individual cookie count.
class Order_Cookies(db.Model):
    __tablename__ = 'order_cookies'
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    cookie_id = db.Column(db.Integer, db.ForeignKey('cookies.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)

    orders = db.relationship('Orders', back_populates='cookies')
    cookies = db.relationship('Cookies', back_populates = 'orders')
    
    @property
    def price(self):
        return self.quantity * self.cookies.price
    
    def to_dict(self):
        return {
            "order_id": self.order_id,
            "cookie_name": self.cookies.cookie_name,
            "quantity": self.quantity,
            "price": self.price
        }

if __name__ == "__main__":
    # Run this file directly to create the database tables.
    print("Creating database tables...")
    db.create_all()
    print("Done!")