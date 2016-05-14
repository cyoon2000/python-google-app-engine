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

# Resort data instance
resorts_instance = model.ResortsList()

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
    # resorts = model.ResortsList.find_all_resorts(resorts_model)
    resorts = model.ResortsList.find_all_resorts(resorts_instance)
    # results = [data.serialize_resort_summary(r) for r in resorts_data]
    results = model.ResortsList.serialize_resorts(resorts_instance, resorts)
    return jsonify(results=results)


@app.route('/resorts/<resortname>')
def show_resort_by_name(resortname):
    # resort = data.find_resort(resorts_data, resortname)
    resort = model.ResortsList.find_resort_by_name(resorts_instance, resortname)
    # resort = model.ResortsList.get_resort_detail(resorts_instance, resortname)

    if not resort:
        return 'Sorry, Invalid Request', 400

    resort_info = model.ResortInfo(resort)

    # units = data.find_units_by_resort_name(units_data, resortname)
    units = model.ResortsList.find_units_by_resort_name(resorts_instance, resortname)
    resort_info.set_units(units)

    profile_photo = model.ResortsList.find_profile_photo_by_resort_name(resorts_instance, resortname)
    resort_info.set_profile_photo(profile_photo)

    # photos = data.find_photos_by_resort_name(photos_data, resortname)
    photos = model.ResortsList.find_photos_by_resort_name(resorts_instance, resortname)
    resort_info.set_photos(photos)


# results = data.serialize_resort_detail(resort, units, photos_by_resort_dict[resortname])
#     results = model.ResortsList.serialize_resort_detail(resorts_instance, resort)
    results = resort_info.serialize_resort_info()
    return jsonify(results=results)