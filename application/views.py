from application import model, get_model

# Import the Flask Framework
from flask import request
from flask import jsonify

from flask import current_app, Blueprint, redirect, render_template, request, url_for
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


#############################################
# Sample App

# [START list]
@api.route("/")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    entries, next_page_token = get_model().list(cursor=token)

    return render_template(
        "list.html",
        entries=entries,
        next_page_token=next_page_token)
# [END list]

@api.route('/<id>')
def view(id):
    entry = get_model().read(id)
    return render_template("view.html", entry=entry)


# [START add]
@api.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        entry = get_model().create(data)

        return redirect(url_for('.view', id=entry['id']))

    return render_template("form.html", action="Add", entry={})
# [END add]


@api.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    entry = get_model().read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        entry = get_model().update(data, id)

        return redirect(url_for('.view', id=entry['id']))

    return render_template("form.html", action="Edit", entry=entry)


@api.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))