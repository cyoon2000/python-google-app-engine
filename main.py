"""`main` is the top level module for your Flask application."""
import data
import model
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
    resorts = model.find_all_resorts()
    results = model.serialize_resorts(resorts)
    return jsonify(results=results)


@app.route('/resorts/<resortname>')
def show_resort_by_name(resortname):

    resort = model.find_resort_by_name(resortname)

    if not resort:
        return 'Sorry, Invalid Request', 400

    resort_info = model.ResortInfo(resort)

    units = model.find_units_by_resort_name(resortname)
    resort_info.set_units(units)

    profile_photo = model.find_profile_photo_by_resort_name(resortname)
    resort_info.set_profile_photo(profile_photo)

    photos = model.find_photos_by_resort_name(resortname)
    resort_info.set_photos(photos)

    results = resort_info.serialize_resort_info()
    return jsonify(results=results)



# @app.route('/resorts/<resortname>/<typename>')
# def show_unit_detail(resortname, typename):
#     unit = model.ResortsList.find_unit_by_name(resorts_instance, typename)
#
#     if not unit:
#         return 'Sorry, Invalid Request', 400
#
#     unit_info = model.UnitInfo(unit)
#     #results = unit_info.serialize_resort_info()
#     results = model.UnitInfo.serialize_unit_summary(unit)
#     return jsonify(results=results)