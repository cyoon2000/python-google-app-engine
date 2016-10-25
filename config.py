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
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usr:pwd@100.200.300.400/bookingdb'
SQLALCHEMY_POOL_RECYCLE = 280
SQLALCHEMY_POOL_TIMEOUT = 20

# Mongo configuration
# If using mongolab, the connection URI is available from the mongolab control
# panel. If self-hosting on compute engine, replace the values below.
#MONGO_URI = \
#    'mongodb://user:password@host:27017/database'

