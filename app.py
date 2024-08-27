from flask import Flask, request
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import db
import users
import psycopg2
app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# Returns content
@app.route("/")
def home():
    return "That's the way the cookie crumbles!"

@app.route('/register', methods=['GET','POST'])
def register():
    if (request.method == 'POST' 
        and 'email' in request.form 
        and 'password' in request.form):

        # Retreive and verify information
        email = request.form.get("email")
        email, email_valid = users.is_email_valid(email)
        if not email_valid: 
            return email
        password = request.form.get("password")
        password, password_valid = users.is_password_valid(password)
        if not password_valid: 
            return password
        
        # Hash password
        password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        return db.user_register(email, password)
    elif request.method == 'POST':
        return "Please fill out the form!"
    return "What you getting at?"

@app.route('/login', methods=['GET','POST'])
def login():
    if (request.method == 'POST' 
        and 'email' in request.form 
        and 'password' in request.form):
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.user_read(email)
        if not user: 
            return "Account with this email doesn't exist. Please try again."
        elif not bcrypt.check_password_hash(user["password"], password):
            return "Password is incorrect. Please try again."
        else:
            return dict(user)
    elif request.method == 'POST':
        return "Please fill out the form!"
    return "What you getting at?"

@app.route('/users', methods=['POST'])
def create():
    email = request.form.get("email")
    password = request.form.get("password")
    return db.user_create(email, password)

# Show account based on id.
@app.route('/users/<id>', methods=['GET'])
def read(id):
    return db.user_read_by_id(id)

# Update account based on id.
@app.route('/users/<id>', methods=['PATCH'])
def update(id):
    email = request.form.get("email")
    password = request.form.get("password")
    return db.user_update_by_id(id, email, password)

# Delete account based on id.
@app.route('/users/<id>', methods=['DELETE'])
def delete(id):
    return db.user_delete_by_id(id)
