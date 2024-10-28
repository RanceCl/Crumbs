from random import randrange
from flask import request, jsonify
from flask_cors import CORS

from ..models import Users, Orders, Payment_Types, Customers, Cookies, Cookie_Inventory, Order_Cookies
import psycopg2

from .. import db

from . import dev_tests
from ..auth.routes import register


# ----------------------------------------- Dev Tests -----------------------------------------
cookie_list = [
    {
        "cookie_name": "Adventurefuls", "price": 6.00,
        "description": "Indulgent brownie-inspired cookies topped with caramel flavored crème with a hint of sea salt.",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage.coreimg.png/1693317691596/meetthecookies-graphics-hybridadventurefuls-255x255.png"},
    {
        "cookie_name": "Caramel Chocolate Chip", "price": 6.00, 
        "description": "Gluten free! Chewy cookies with rich caramel, semisweet chocolate chips, and a hint of sea salt.",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy.coreimg.png/1688655459226/21-marcomm-meetthecookies-graphics-abccaramelchocolatechip-255x255.png"},
    {
        "cookie_name": "Caramel deLites", "price": 6.00, 
        "description": "Crisp cookies with caramel, coconut, and chocolaty stripes .",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1168943426.coreimg.png/1693315719665/meetthecookies-graphics-hybridsamoascarameldelites-255x255.png"},
    {
        "cookie_name": "Peanut Butter Sandwich | Do-si-dos", "price": 6.00, 
        "description": "Crunchy oatmeal sandwich cookies with peanut butter filling.",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1034315555.coreimg.png/1725455442556/meetthecookies-graphics-hybridpeanutbuttersandwichdosidos-255x255.png"},
    {
        "cookie_name": "Girl Scout S'mores", "price": 6.00, 
        "description": "Crunchy graham sandwich cookies with chocolate and marshmallow filling.",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1756629764.coreimg.png/1693315770522/meetthecookies-graphics-lbbsmores-255x255.png"},
    {
        "cookie_name": "Lemonades", "price": 6.00, 
        "description": "Savory, refreshing shortbread cookies topped with a tangy lemon-flavored icing.",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_973166062.coreimg.png/1688655543113/meetthecookies-graphics-abclemonades-255x255.png"},
    {
        "cookie_name": "Lemon-Ups", "price": 6.00, 
        "description": "Crispy lemon cookies baked with inspiring messages.",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1787644668.coreimg.png/1693315792917/meetthecookies-graphics-lbblemonups-255x255.png"},
    {
        "cookie_name": "Peanut Butter Patties", "price": 6.00, 
        "description": "Crispy cookies layered with peanut butter and covered with a chocolaty coating.",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_435681049.coreimg.png/1693315815634/meetthecookies-graphics-hybridpeanutbutterpattiestagalongs-255x255.png"},
    {
        "cookie_name": "Thin Mints", "price": 6.00, 
        "description": "Crisp, chocolate cookies dipped in a delicious mint chocolaty coating.",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1574458209.coreimg.png/1693315839299/meetthecookies-graphics-hybridthinmints-255x255.png"},
    {
        "cookie_name": "Toast-Yays", "price": 6.00, 
        "description": "Yummy toast-shaped cookies full of French toast flavor and dipped in delicious icing.",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1639980537.coreimg.png/1693230514183/meetthecookies-graphics-abctoast-yay-255x255.png"},
    {
        "cookie_name": "Toffee-tastic", "price": 6.00, 
        "description": "Gluten free! Rich, buttery cookies with sweet, crunchy toffee bits.",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_1157222513.coreimg.png/1693316248715/meetthecookies-graphics-lbbtoffeetastic-255x255.png"},
    {
        "cookie_name": "Trefoils", "price": 6.00, 
        "description": "Iconic shortbread cookies inspired by the original Girl Scout Cookie recipe.",
        "picture_url": "https://www.girlscouts.org/en/cookies/cookie-flavors/_jcr_content/root/container/gridsystem_copy/par_0/textandimage_copy_750886972.coreimg.png/1713984333162/meetthecookies-graphics-hybridshortbreadtrefoils-255x255.png"}
    ]

payment_list = [
    {"payment_type_name": "Cash"},
    {"payment_type_name": "Credit"},
    {"payment_type_name": "Venmo"},
    {"payment_type_name": "PayPal"}
]

def create_db():
    """Creates the database."""
    db.create_all()

def drop_db():
    """Drops the database."""
    db.drop_all()

def recreate_db():
    """Same as running drop_db() and create_db()."""
    drop_db()
    create_db()

# Order Cookie initialization
def add_order_cookie(order_id, cookie_id, quantity):
    new_order_cookie = Order_Cookies(order_id=order_id,
                                     cookie_id=cookie_id,
                                     quantity=quantity)
    db.session.add(new_order_cookie)
    db.session.commit()
    return new_order_cookie.order_id, new_order_cookie.cookie_id

# For each order, add a random amount of cookies
def populate_order_cookies(order_id):
    for i in range(1,12, randrange(1, 6)):
        add_order_cookie(order_id, i, randrange(0, 10))
    return None

# Order initialization
def add_order(customer_id, payment_id):
    new_order = Orders(customer_id=customer_id,
                       payment_id=payment_id)
    db.session.add(new_order)
    db.session.commit()
    return new_order.id

# For each customer, add four orders
def populate_orders(customer_id):
    for _ in range(4):
        new_order_id = add_order(customer_id, 0)
        populate_order_cookies(new_order_id)
    return None

# Customer initialization
def add_customer(customer_name, user_id):
    new_customer = Customers(first_name=customer_name[0],
                            last_name=customer_name[1],
                            user_id=user_id)
    #current_user.append(new_customer)
    db.session.add(new_customer)
    db.session.commit()
    return new_customer.id

@dev_tests.route('/populate_customers', methods=['GET','POST'])
def populate_customers():
    names = [
        ["Chad", "GPT"], ["Jim", "Anderson"], ["Known","Lastname"], 
        ["Jane", "Doe"], ["Don", "Nots"], ["Abe", "Lincoln"],
        ["Corey", "House"], ["Linda", "Ahern"], ["Leanne", "Cavanaugh"],
        ["Noni", "Nonya"], ["Firstname", "Lastname"], ["Best", "Friend"],
        ["Midnight", "White"], ["Marley", "Ahern"], ["Chi-Chi","DBZ"],
        ["Chad", "GPT"]
    ]
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

# Inventory initialization
def add_inventory_cookie(user_id, cookie_id, inventory):
    new_inventory_cookie = Cookie_Inventory(user_id=user_id,
                                     cookie_id=cookie_id,
                                     inventory=inventory)
    db.session.add(new_inventory_cookie)
    db.session.commit()
    return new_inventory_cookie.user_id, new_inventory_cookie.cookie_id

# For each order, add a random amount of cookies
def populate_inventory_cookies(user_id):
    for i in range(1,12, randrange(1, 6)):
        add_inventory_cookie(user_id, i, randrange(100, 200))
    return None

@dev_tests.route('/populate_inventory', methods=['GET','POST'])
def populate_inventory():
    user_ids = [id[0] for id in Users.query.with_entities(Users.id).all()]
    for user_id in user_ids:
        populate_inventory_cookies(user_id)
            
    return "Inventory populated"

# User initialization
def add_user(email, password, first_name, last_name):
    password_confirm = password
    new_user = Users(email=email, 
                     first_name=first_name, 
                     last_name=last_name)
    if not new_user.set_password(password, password_confirm):
        db.session.add(new_user)
        db.session.commit()
    return None

# @dev_tests.route('/populate_users', methods=['GET','POST'])
# def populate_users():
#     add_user("chadgregpaulthompson@gmail.com", "Ch@t3PT", "Chad", "GPT")
#     add_user("anonymous@email.com", "S3cr3t P@$$word", "Anonymous", "NoLastName")
#     add_user("known@email.com", "S33n P@$$word", "Known", "HasLastName")
#     add_user("elmo@email.com", "B33G B1rd$", "Elmo", "Sesame")

@dev_tests.route('/populate_users', methods=['GET','POST'])
def populate_users():
    add_user("tina@gmail.com", "password123!", "Tina", "Clawson")
    add_user("eno@gmail.com", "password123!", "Eno", "Clawson")
    add_user("waffle@gmail.com", "password123!", "Waffle", "Denig")
    add_user("agnes@gmail.com", "password123!", "Agnes", "Hale")
    

    return "Table populated"
    # return redirect(url_for('login'))

# Database initialization
@dev_tests.route('/init_db', methods=['GET','POST'])
def initialize_db():
    drop_db()
    create_db()
    for cookie_entry in cookie_list:  
        new_cookie = Cookies(
            cookie_name=cookie_entry["cookie_name"],
            price=cookie_entry["price"],
            description=cookie_entry["description"],
            picture_url=cookie_entry["picture_url"])
        db.session.add(new_cookie)
        db.session.commit()
    # Add payments, including default.
    new_payment_type = Payment_Types(id=0, payment_type_name="Unspecified")
    db.session.add(new_payment_type)
    db.session.commit()
    for payment_entry in payment_list:  
        new_payment_type = Payment_Types(payment_type_name=payment_entry["payment_type_name"])
        db.session.add(new_payment_type)
        db.session.commit()
    populate_users()
    # Quickly register for quicker reinitialization of the database.
    if('email' in request.form and 
       'password' in request.form and 
       'password_confirm' in request.form and 
       'first_name' in request.form and 
       'last_name' in request.form):
        register()
    populate_inventory()
    populate_customers()

    return "Database CREATED!"
