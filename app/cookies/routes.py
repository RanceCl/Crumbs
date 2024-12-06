from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Cookies
import psycopg2

from .. import db

from . import cookies


# ----------------------------------------- COOKIES -----------------------------------------
#Get all of the cookies
@cookies.route('/', methods=['GET'])
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
    return {"status": "success", 'cookies': cookies_list}, 200

# Show single cookie information
@cookies.route('/<cookie_id>', methods=['GET'])
def cookie_read(cookie_id):
    cookie = Cookies.query.filter_by(id=cookie_id).first()
    if not cookie:
        return "I'm sorry, " + cookie_id + " doesn't exist. :("
    return cookie.to_dict()

# Add cookie from cookie page
@cookies.route('/', methods=['POST'])
@login_required
def add_cookie():
    # A new cookie can only be placed if the customer id is provided and a valid payment type is also provided.
    if ('cookie_name' in request.form and 'price' in request.form):
        cookie_name = request.form.get("cookie_name")

        # Make sure that the cookie doesn't already exist.
        cookie = Cookies.query.filter_by(cookie_name=cookie_name).first()
        if cookie:
            return jsonify({"status": "error", "message": "Cookie " + cookie_name + " already exists."}), 400
        
        new_cookie = Cookies(
            cookie_name = cookie_name,
            description = request.form.get("description", ""),
            price = float(request.form.get("price")),
            picture_url = request.form.get("picture_url", "")
            )

        db.session.add(new_cookie)
        db.session.commit()
        return jsonify(new_cookie.to_dict()), 200
    return jsonify({"status": "error", "message": "Please fill out the form!"}), 400

# Update cookies
@cookies.route('/<cookie_id>', methods=['PATCH'])
@login_required
def update_cookie(cookie_id):
    # Make sure that the cookie exists.
    cookie = Cookies.query.filter_by(id=cookie_id).first()
    if not cookie:
        return jsonify({"status": "error", "message": "cookie " + cookie_id + " not found."}), 404
    
    # Only edit properties requested.
    if ("cookie_name" in request.form):
        cookie.description = request.form.get("cookie_name")
    if ("description" in request.form):
        cookie.description = request.form.get("description")
    if ("price" in request.form):
        cookie.price = float(request.form.get("price"))
    if ("picture_url" in request.form):
        cookie.picture_url = request.form.get("picture_url")

    db.session.commit()
    return jsonify(cookie.to_dict()), 200

# Delete cookies
@cookies.route('/<cookie_id>', methods=['DELETE'])
@login_required
def delete_cookie(cookie_id):
    # Make sure that the cookie exists.
    cookie = Cookies.query.filter_by(id=cookie_id).first()
    if not cookie:
        return jsonify({"status": "error", "message": "cookie " + cookie_id + " not found."}), 404
    db.session.delete(cookie)
    db.session.commit()
    return jsonify({"status": "success", "message": "cookie " + cookie_id + " deleted."}), 200
