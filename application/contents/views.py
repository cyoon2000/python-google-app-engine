from flask import jsonify
from flask import current_app, Blueprint, redirect, render_template, request, url_for
from application.contents import model
from application.common import utils

api = Blueprint('api', __name__)

@api.route('/resorts')
#@requires_auth
def show_resorts():
    resorts = model.find_all_resorts()
    resort_info_list = []
    for resort in resorts:
        resort_info = model.ResortInfo(resort, None, None)
        resort_info_list.append(resort_info)

    results = model.serialize_resort_info_list(resort_info_list)
    return jsonify(results=results)


@api.route('/resorts/<resortname>')
def show_resort_by_name(resortname):

    resort = model.find_resort_by_name(resortname)
    if not resort:
        return 'Sorry, Invalid Request', 400

    results = model.ResortInfo(resort, None, None).serialize_resort_info()
    return jsonify(results=results)


@api.route('/resorts/<resortname>/<typename>')
def show_unit_detail(resortname, typename):

    begin_date = utils.get_begin_date(request)
    end_date = utils.get_end_date(request)

    unit = model.find_unit_by_name(typename)
    if not unit:
        return 'Sorry, Invalid Request', 400

    unit_info = model.UnitInfo(unit, begin_date, end_date)
    results = unit_info.serialize_unit_detail()
    return jsonify(results=results)
