""" Development Configurations """
# SQL
SQLALCHEMY_DATABASE_URI = ""
SQLALCHEMY_TRACK_MODIFICATIONS = False
PREFERRED_URL_SCHEME = "https"

# Log
APP_LOG_FILE = 'log/app.log'
APP_LOG_LEVEL = 'DEBUG'

# App Session Setting
SECRET_KEY = ""
SESSION_TYPE = 'filesystem'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_PERMANENT = True

# AWS
S3_BUCKET = "tech.chocolatepie"
S3_KEY = ""
S3_SECRET_ACCESS_KEY = ""
S3_LOCATION = "http://{}.s3.amazonaws.com/".format(S3_BUCKET)

# Image temporary directory
IMG_DIR = "/home/info_sys/info_sys_api/tmp/"

# Firebase Cloud Messaging(FCM)
FSM_API_KEY = ""
