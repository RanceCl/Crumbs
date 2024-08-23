from flask import Flask, request
from flask_cors import CORS
import db
import psycopg2
app = Flask(__name__)
CORS(app)

# Returns content
@app.route("/")
def home():
    return "That's the way the cookie crumbles!"

@app.route('/users/create', methods=['POST'])
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
    return db.user_update_by_id(email, password)

# Delete account based on id.
@app.route('/users/<id>', methods=['DELETE'])
def delete(id):
    return db.user_delete_by_id(id)

