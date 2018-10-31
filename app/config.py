""" Development Configurations """
from datetime import timedelta

# SQL
SECRET_KEY = ""
SQLALCHEMY_DATABASE_URI = ""
SQLALCHEMY_TRACK_MODIFICATIONS = False
PREFERRED_URL_SCHEME = "https"

SESSION_TYPE = 'filesystem'

# Log
APP_LOG_FILE = 'log/app.log'
APP_LOG_LEVEL = 'DEBUG'

# App Session Setting
SESSION_COOKIE_SECURE = True
PERMANENT_SESSION_LIFETIME = timedelta(days=30)
