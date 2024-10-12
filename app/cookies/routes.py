from flask import request, jsonify
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
    return {'cookies': cookies_list}, 200

# Show single cookie information
@cookies.route('/<cookie_name>', methods=['GET'])
def cookie_read(cookie_name):
    cookie = Cookies.query.filter_by(cookie_name=cookie_name).first()
    if not cookie:
        return "I'm sorry, " + cookie_name + " doesn't exist. :("
    return {'id': cookie.id, 
            'name': cookie.cookie_name, 
            'price': cookie.price, 
            'description': cookie.description, 
            'picture': cookie.picture_url}
