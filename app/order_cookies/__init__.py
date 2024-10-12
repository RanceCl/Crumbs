from flask import Blueprint

order_cookies = Blueprint('order_cookies', __name__)

from . import routes