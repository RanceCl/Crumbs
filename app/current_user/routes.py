from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Users, Orders, Customers, Cookies, Cookie_Inventory, Cookie_Orders
import psycopg2

from .. import db, login_manager

from . import current_user as cur_user


# ----------------------------------------- User Info -----------------------------------------
#Use Flask-Login to get current user
@cur_user.route('/', methods=['GET'])
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
