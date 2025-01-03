'''
host="localhost"
database="crumbs_db"
user="annclawson"
password="postgres"

print('postgresql://postgres:postgres@localhost/crumbs_db')
print('postgresql://'+user+':'+password+'@'+host+'/'+database)
'''
import os
import load_env_var
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    TESTING = False 
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://'+os.environ["POSTRGRES_USER"]+':'+os.environ["POSTRGRES_PASSWORD"]+'@'+os.environ["POSTRGRES_HOST"]+'/'+os.environ["POSTRGRES_DATABASE"]
    #PERMANENT_SESSION_LIFETIME = timedelta(minutes=1)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,

    'default': DevelopmentConfig
}