from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from config import Config


bcrypt = Bcrypt()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})
    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    register_blueprints(app)

    return app

def register_blueprints(app):
    with app.app_context():
        from .auth import auth as auth_bp
        app.register_blueprint(auth_bp)
        
        from .cookies import cookies as cookies_bp
        app.register_blueprint(cookies_bp, url_prefix='/cookies')

        from .order_cookies import order_cookies as order_cookies_bp
        app.register_blueprint(order_cookies_bp, url_prefix='/orders')

        from .current_user import current_user as current_user_bp
        app.register_blueprint(current_user_bp, url_prefix='/current-user')

        from .customers import customers as customers_bp
        app.register_blueprint(customers_bp, url_prefix='/customers')

        from .dev_tests import dev_tests as dev_tests_bp
        app.register_blueprint(dev_tests_bp, url_prefix='/dev_tests')

        from .inventory import inventory as inventory_bp
        app.register_blueprint(inventory_bp, url_prefix='/users/inventory')

        from .orders import orders as orders_bp
        app.register_blueprint(orders_bp, url_prefix='/orders')

        from .users import users as users_bp
        app.register_blueprint(users_bp, url_prefix='/users')