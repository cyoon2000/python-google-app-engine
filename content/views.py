from content import model

# Import the Flask Framework
from flask import request
from flask import jsonify

from flask import current_app, Blueprint
api = Blueprint('api', __name__)

# @api.route('/')
# def hello():
#     """Return a friendly HTTP greeting."""
#     return 'Hello World!'


@api.route('/resorts')
#@requires_auth
def show_resorts():
    resorts = model.find_all_resorts()
    results = model.serialize_resorts(resorts)
    return jsonify(results=results)


@api.route('/resorts/<resortname>')
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


@api.route('/resorts/<resortname>/<typename>')
def show_unit_detail(resortname, typename):

    begin_date = request.args.get('begin')
    end_date = request.args.get('end')

    unit = model.find_unit_by_name(typename)

    if not unit:
        return 'Sorry, Invalid Request', 400

    # unit_info = model.UnitInfo(unit)
    results = model.serialize_unit_detail(unit, begin_date, end_date)
    return jsonify(results=results)
