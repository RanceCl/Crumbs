from app import create_app
'''
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

if __name__ == '__main__':
    from models import *
    from routes import *
    app.run(debug=True)
'''

app = create_app()

if __name__ == '__main__':
    from app.models import *
    #from app.routes import *
    app.run(debug=True)