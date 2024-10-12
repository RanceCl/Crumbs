from flask import request, jsonify
from flask_login import current_user, login_required
from flask_cors import CORS

from ..models import Users, Orders, Customers, Cookies, Cookie_Inventory, Order_Cookies
import psycopg2

from .. import db, login_manager

from . import order_cookies

# ----------------------------------------- Cookie Orders -----------------------------------------
