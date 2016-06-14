# The secret key is used by Flask to encrypt session cookies.
SECRET_KEY = 'secret'

# There are three different ways to store the data in the application.
# You can choose 'datastore', 'cloudsql', or 'mongodb'. Be sure to
# configure the respective settings for the one you choose below.
# You do not have to configure the other data backends. If unsure, choose
# 'datastore' as it does not require any additional configuration.
DATA_BACKEND = 'cloudsql'

# Google Cloud Project ID. This can be found on the 'Overview' page at
# https://console.developers.google.com
PROJECT_ID = 'gokitebaja-flask'

# SQLAlchemy configuration
# Replace user, pass, host, and database with the respective values of your
# Cloud SQL instance.
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://pythonapp:kite123@173.194.86.223/guestbook'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@104.198.198.22/booking-db'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@104.198.198.22/booking-db?unix_socket=/cloudsql/gokitebaja-flask:us-central1:booking-db'
#  SQLALCHEMY_DATABASE_URI =  'mysql+pymysql://user:password@104.198.198.22/booking-db'


# Mongo configuration
# If using mongolab, the connection URI is available from the mongolab control
# panel. If self-hosting on compute engine, replace the values below.
#MONGO_URI = \
#    'mongodb://user:password@host:27017/database'
