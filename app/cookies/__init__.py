from flask import Blueprint

cookies = Blueprint('cookies', __name__)

from . import routes