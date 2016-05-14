"""`main` is the top level module for your Flask application."""
import data
import logging

# Import the Flask Framework
from flask import jsonify
from flask import Flask
from flask.ext.cors import CORS #, cross_origin

app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

# CORS support
CORS(app)

# TODO - find a way to load data only once
resorts_data = data.resorts()
units_data = data.units()
photos_by_resort_dict = data.photos_by_resort_dict()
profile_photo_dict = data.profile_photo_dict()

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


@app.route('/resorts')
#@requires_auth
def show_resorts():
    # resort_list = data.find_all_resorts()
    results = [data.serialize_resort_summary(r) for r in resorts_data]
    # results = data.serialize_resorts(resorts)
    return jsonify(results=results)


@app.route('/resorts/<resortname>')
def show_resort_by_name(resortname):
    resort = data.find_resort(resorts_data, resortname)
    if not resort:
        return 'Sorry, Invalid Request', 400
    units = data.find_units_by_resort_name(units_data, resortname)
    # photos = data.find_photos_by_resort_name(photos_data, resortname)
    results = data.serialize_resort_detail(resort, units, photos_by_resort_dict[resortname])
    return jsonify(results=results)