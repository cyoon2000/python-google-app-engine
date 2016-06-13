"""`main` is the top level module for your Flask application."""
import content
import config

# from flask import Flask
# from flask.ext.cors import CORS #, cross_origin

#app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

# CORS support
#CORS(app)


app = content.create_app(config)


# This is only used when running locally. When running live, gunicorn runs
# the application.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)