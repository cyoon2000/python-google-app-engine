import json
from . import get_model
from . import model

from datetime import datetime
from flask import current_app, Blueprint, redirect, render_template, request, url_for
from flask import jsonify, json
from flask_wtf import Form
#from wtforms.fields.html5 import DateField

bookings_api = Blueprint('bookings', __name__, template_folder='templates')

@bookings_api.route("/")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    bookings, next_page_token = get_model().list(cursor=token)

    try: return render_template(
        "list.html",
        bookings=bookings,
        next_page_token=next_page_token)
    except TemplateNotFound:
        abort(404)

@bookings_api.route('/<id>')
def view(id):
    booking = get_model().read(id)
    return render_template("view.html", booking=booking)


@bookings_api.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        booking = get_model().create(data)

        return redirect(url_for('.view', id=booking['id']))

    return render_template("form.html", action="Add", booking={})


@bookings_api.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    booking = get_model().read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        booking = get_model().update(data, id)

        return redirect(url_for('.view', id=booking['id']))

    return render_template("form.html", action="Edit", booking=booking)


@bookings_api.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))


# Returns JSON
@bookings_api.route("/resorts")
def list_resort():
    resorts = model.list_resorts()
    for resort in resorts:
        print resort.name
    return "OK"


@bookings_api.route("/index")
def index():
    return jsonify({'resorts': model.Resort.query.all()})


# Returns JSON
@bookings_api.route("/resorts/<id>/unitgroups")
def list_unitgroups(id):
    results = model.list_unitgroups(id)
    return jsonify(results=results)


# Returns JSON
@bookings_api.route("/resorts/<id>/units")
def list_units(id):
    results = model.list_units(id)
    return jsonify(results=results)


# Return JSON
# Sample data: http://localhost:8080/bookings/availability/unit/10?begin=2016-07-01&end=2016-07-10
@bookings_api.route("/availability/unit/<id>")
def list_availability(id):
    begin_date = request.args.get('begin')
    end_date = request.args.get('end')
    # TODO - set begin_date = today, end_date = today + 14 days
    if not begin_date or not end_date:
        begin_date = '2016-07-01'
        end_date = '2016-07-14'

    c = model.list_availability(id, begin_date, end_date)
    results = [serialize_availability(r) for r in c]
    return jsonify(data=results)


@bookings_api.route('/availability/<id>/edit', methods=['GET', 'POST'])
def edit_availability(id):
    avail = model.read_availability(id)
    # TODO - 400 for invalid id

    if request.method == 'POST':
        avail.unit_id = request.json.get('unit_id')
        avail.date_slot = request.json.get('date_slot')
        avail.status = request.json.get('status')
        avail = model.update(avail, id)

    return jsonify(data=serialize_availability(avail))



def serialize_availability(availability):
    return {
        'id': availability.id,
        'date_slot': availability.date_slot.isoformat(),
        'month': availability.date_slot.month,
        'day': availability.date_slot.day,
        'weekday': availability.date_slot.weekday(), # Monday is 0 and Sunday is 6
        'booked': False if availability.status == 1 else True,
        'status': availability.status,
        'booking_id': availability.booking_id
    }