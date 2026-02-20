import os

class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'SAHIL@2910'
    MYSQL_DB = 'seathive_db'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = True
