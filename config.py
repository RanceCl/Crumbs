'''
host="localhost"
database="crumbs_db"
user="annclawson"
password="postgres"

print('postgresql://postgres:postgres@localhost/crumbs_db')
print('postgresql://'+user+':'+password+'@'+host+'/'+database)
'''
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://annclawson:postgres@localhost/crumbs_db'