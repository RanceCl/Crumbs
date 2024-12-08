from enum import IntEnum
from . import db, bcrypt, login_manager
from flask_login import UserMixin
from . import user_validate
from sqlalchemy import func

class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0)
    

    cookies = db.relationship("Cookie_Inventory", back_populates = "users", cascade="all, delete-orphan")
    customers = db.relationship("Customers", back_populates = "users", cascade="all, delete-orphan")
    orders = db.relationship("Orders", back_populates="users", cascade="all, delete-orphan")

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
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        return None
    
    # Make sure password matches
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    # Update inventory
    def update_cookie_inventory(self):
        all_cookies = Cookies.query.all()
        existing_cookie_inventories = {uc.cookie_id: uc for uc in self.cookies}
        
        for cookie in all_cookies:
            if cookie.id not in existing_cookie_inventories:
                new_cookie_inventory = Cookie_Inventory(user_id=self.id, cookie_id=cookie.id, inventory=0)
                db.session.add(new_cookie_inventory)
        db.session.commit()
    
    # Get current balance of payment types from finalized orders and finalized payements (though order may be incomplete)
    @property
    def actual_balance(self):
        """
        Aggregates the total balance for each payment type:
        - Includes orders with `order_status` set to "Complete".
        - Includes orders with `payment_status` set to "Complete" but `order_status` is incomplete.
        Returns a dictionary with payment types as keys and total balances as values.
        """
        completed_status_orders = (
            db.session.query(
                Payment_Types.payment_type_name,
                func.sum(Order_Cookies.quantity * Cookies.price).label("total_cost"),
            )
            .join(Orders, Orders.payment_id == Payment_Types.id)
            .join(Order_Cookies, Order_Cookies.order_id == Orders.id)
            .join(Cookies, Cookies.id == Order_Cookies.cookie_id)
            .filter(
                Orders.user_id == self.id,
                Orders.order_status_stored == "Complete",
            )
            .group_by(Payment_Types.payment_type_name)
            .all()
        )

        completed_payment_orders = (
            db.session.query(
                Payment_Types.payment_type_name,
                func.sum(Order_Cookies.quantity * Cookies.price).label("total_cost"),
            )
            .join(Orders, Orders.payment_id == Payment_Types.id)
            .join(Order_Cookies, Order_Cookies.order_id == Orders.id)
            .join(Cookies, Cookies.id == Order_Cookies.cookie_id)
            .filter(
                Orders.user_id == self.id,
                Orders.order_status_stored != "Complete",  # Avoid duplication with completed orders
                Orders.payment_status_stored == "Complete",  # Include orders with completed payment only
            )
            .group_by(Payment_Types.payment_type_name)
            .all()
        )

        # Combine results into a single dictionary
        balance_dict = {}
        for payment_type, total_cost in completed_status_orders:
            balance_dict[payment_type] = total_cost or 0.0

        for payment_type, total_cost in completed_payment_orders:
            if payment_type in balance_dict:
                balance_dict[payment_type] += total_cost or 0.0
            else:
                balance_dict[payment_type] = total_cost or 0.0

        return balance_dict

    @property
    def projected_balance(self):
        """
        Aggregates the projected balance for each payment type from non-completed orders.
        Returns a dictionary with payment types as keys and total balances as values.
        """
        pending_orders = (
            db.session.query(
                Payment_Types.payment_type_name,
                func.sum(Order_Cookies.quantity * Cookies.price).label("total_cost"),
            )
            .join(Orders, Orders.payment_id == Payment_Types.id)
            .join(Order_Cookies, Order_Cookies.order_id == Orders.id)
            .join(Cookies, Cookies.id == Order_Cookies.cookie_id)
            .filter(Orders.user_id == self.id, Orders.order_status_stored == ("Incomplete"))
            .group_by(Payment_Types.payment_type_name)
            .all()
        )

        return {payment_type: total_cost or 0.0 for payment_type, total_cost in pending_orders}

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "balance": self.balance,
            "actual_balance": self.actual_balance,  
            "projected_balance": self.projected_balance,
        }


# User loader for flask-login
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

class Cookies(db.Model):
    __tablename__ = "cookies"
    id = db.Column(db.SmallInteger, primary_key=True)
    cookie_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String, nullable=False, default="")
    price = db.Column(db.Float, nullable=False, default=0)
    picture_url = db.Column(db.String, nullable=False, default="")

    users = db.relationship("Cookie_Inventory", back_populates = "cookies", cascade="all, delete-orphan")
    orders = db.relationship("Order_Cookies", back_populates = "cookies", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "cookie_name": self.cookie_name,
            "description": self.description,
            "price": self.price,
            "picture_url": self.picture_url
        }
    
# Each user"s individual cookie count.
class Cookie_Inventory(db.Model):
    __tablename__ = "cookie_inventory"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    cookie_id = db.Column(db.SmallInteger, db.ForeignKey("cookies.id"), primary_key=True)
    inventory = db.Column(db.Integer, nullable=False, default=0)

    users = db.relationship("Users", back_populates="cookies")
    cookies = db.relationship("Cookies", back_populates = "users")

    def __init__(self, user_id, cookie_id, inventory):
        self.user_id = user_id
        self.cookie_id = cookie_id
        self.inventory = inventory
    
    # Calculate the projected inventory after the removal of all orders from the current inventory.
    @property
    def projected_inventory(self):
        # Get all of the orders associated with the user. 
        order_cookies = Order_Cookies.query.join(Orders).join(Customers).join(Users).filter(Users.id==self.user_id, Order_Cookies.cookie_id==self.cookie_id, Orders.order_status_stored!="Complete").all()
        #order_cookies = Order_Cookies.query.join(Orders).join(Customers).join(Users).filter(Users.id==self.user_id, Order_Cookies.cookie_id==self.cookie_id).all()
        resulting_quantity = self.inventory
        for order_cookie in order_cookies:
            resulting_quantity -= order_cookie.quantity
        return resulting_quantity
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "cookie_name": self.cookies.cookie_name,
            "picture_url": self.cookies.picture_url,
            "description": self.cookies.description,
            "inventory": self.inventory,
            "projected_inventory": self.projected_inventory
        }
    
class Payment_Types(db.Model):
    __tablename__ = "payment_types"
    id = db.Column(db.Integer, primary_key=True)
    payment_type_name = db.Column(db.String(50), unique=True, nullable=False)

    orders = db.relationship("Orders", back_populates="payment_types", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "payment_type_name": self.payment_type_name
        }

class Customers(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    email = db.Column(db.String(120))

    users = db.relationship("Users", back_populates="customers")
    orders = db.relationship("Orders", back_populates="customers", cascade="all, delete-orphan")
    
    def __init__(self, user_id, first_name=None, last_name=None):
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id
    
    def set_email(self, email):
        # Make sure that email is in a valid format.
        email, email_valid = user_validate.is_email_valid(email)
        if not email_valid: 
            return email
        self.email = email
        return None
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email if self.email else ""
        }

OrderStatus = ["Incomplete", "Complete"]
PaymentStatus = ["Unconfirmed", "Complete", "Incomplete", "Invalid"]
DeliveryStatus = ["Not Sent", "Mailed", "Delivered", "Delayed", "Picked Up"]

# Actual orders for the cookies.
class Orders(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    payment_id = db.Column(db.Integer, db.ForeignKey("payment_types.id"))
    notes = db.Column(db.String, nullable=False, default="")
    date_added = db.Column(db.Date, default=db.func.current_timestamp())
    date_modified = db.Column(db.Date, default=db.func.current_timestamp())
    order_status_stored = db.Column(db.String, nullable=False, default="Incomplete")
    payment_status_stored = db.Column(db.String, nullable=False, default="Incomplete")
    delivery_status_stored = db.Column(db.String, nullable=False, default="Not Sent")
    
    users = db.relationship("Users", back_populates="orders")
    customers = db.relationship("Customers", back_populates="orders")
    cookies = db.relationship("Order_Cookies", back_populates = "orders", cascade="all, delete-orphan")
    payment_types = db.relationship("Payment_Types", back_populates="orders")

    def __init__(self, user_id, customer_id=None, payment_type="Unspecified", notes="", payment_status="Incomplete", delivery_status="Not Sent"):
        self.user_id = user_id
        self.customer_id = customer_id
        self.payment_type_name(payment_type)
        self.payment_status = payment_status
        self.delivery_status = delivery_status
        self.notes = notes
    
    def order_updated(self):
        self.date_modified = db.func.current_timestamp()

    # The getter and setter for the payment_id.
    def payment_type_name(self, new_payment_name):
        payment_type = Payment_Types.query.filter_by(payment_type_name=new_payment_name).first()
        if not payment_type:
            self.payment_id = 0
        else:
            self.payment_id = payment_type.id
        return

    # The getter and setter for the payment status.
    @property
    def payment_status(self):
        return self.payment_status_stored
    
    @payment_status.setter
    def payment_status(self, new_status):
        if new_status in PaymentStatus:
            self.payment_status_stored = new_status
    
    # The getter and setter for the delivery status.
    @property
    def delivery_status(self):
        return self.delivery_status_stored
    
    @delivery_status.setter
    def delivery_status(self, new_status):
        if new_status in DeliveryStatus:
            self.delivery_status_stored = new_status
    
    # When an order is complete, it must alter the actual inventory.
    def complete_order(self):
        user_id = self.users.id
        order_cookies = self.cookies
        for order_cookie in order_cookies:
            cookie_inventory = Cookie_Inventory.query.filter_by(user_id=user_id, cookie_id=order_cookie.cookie_id).first()

            # Make sure that the inventory doesn't get set to a negative value.
            if cookie_inventory:
                if cookie_inventory.inventory >= order_cookie.quantity:
                    cookie_inventory.inventory -= order_cookie.quantity
                # Rollback changes and stop adjusting if adjusting would result in a negative inventory stored.
                else:
                    db.session.rollback()
                    return None
        
        # Add cost of order to the current user's balance if the order can be completed.
        self.users.balance += self.total_cost

        # Only set to complete and commit changes if they won't cause an invalid actual inventory.
        self.order_status_stored = "Complete"
        db.session.commit()

    # The getter and setter for the order status.
    @property
    def order_status(self):
        return self.order_status_stored

    @order_status.setter
    def order_status(self, new_status):
        # The payment status must be set to complete and the delivery status must not indicate an issue before the order status can be set to complete.
        if (new_status == "Complete" 
            and self.payment_status == "Complete" 
            and self.delivery_status != "Not Sent" and self.delivery_status != "Delayed"):
            self.complete_order()
        else:
            self.order_status_stored = "Incomplete"
    
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
            "user_id": self.user_id,
            "customer_id": self.customer_id if self.customer_id else "",
            "customer_first_name": self.customers.first_name if self.customer_id else "",
            "customer_last_name": self.customers.last_name if self.customer_id else "",
            "payment_type": self.payment_types.payment_type_name,
            "total_cost": self.total_cost,
            "notes": self.notes,
            "date_added": self.date_added,
            "date_modified": self.date_modified,
            "order_status": str(self.order_status),
            "payment_status": str(self.payment_status),
            "delivery_status": str(self.delivery_status),
            "order_cookies": self.get_order_cookies()
        }

# Each order's individual cookie count.
class Order_Cookies(db.Model):
    __tablename__ = "order_cookies"
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), primary_key=True)
    cookie_id = db.Column(db.Integer, db.ForeignKey("cookies.id"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)

    orders = db.relationship("Orders", back_populates="cookies")
    cookies = db.relationship("Cookies", back_populates = "orders")
    
    @property
    def price(self):
        return self.quantity * self.cookies.price
    
    def to_dict(self):
        return {
            "order_id": self.order_id,
            "cookie_name": self.cookies.cookie_name,
            "cookie_id": self.cookies.id,
            "quantity": self.quantity,
            "price": self.price
        }

if __name__ == "__main__":
    # Run this file directly to create the database tables.
    print("Creating database tables...")
    db.create_all()
    print("Done!")