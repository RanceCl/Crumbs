from flask import Blueprint

quick_orders = Blueprint('quick_orders', __name__)

from . import routes