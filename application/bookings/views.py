import flask
import json
import logging
from . import get_model
from . import model, forms

from datetime import datetime
from datetime import timedelta
from flask import current_app, Blueprint, session, redirect, render_template, request, url_for, flash
from flask import jsonify, json
from flask_wtf import Form
#from wtforms.fields.html5 import DateField

bookings_api = Blueprint('bookings', __name__, template_folder='templates')

DEFAULT_NEXT_DAYS = 14


@bookings_api.before_request
def before_request():
    # TODO - save resort_id in session upon login
    session['resort_id'] = 4


# @bookings_api.before_request
def before_request2():
    g.user = None
    g.resort = None

    # if 'user_id' in session:
    #     g.user = model.User.query.get(session['user_id'])
    if 'resort_id' in session:
        g.resort = model.Resort.query.get(session['resort_id'])


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

    # if request.method == 'POST':
    #     data = request.form.to_dict(flat=True)
    #     booking = get_model().create(data)
    #
    #     return redirect(url_for('.view', id=booking['id']))
    # return render_template("form.html", action="Add", booking={})

    form = forms.BookingForm()
    units = model.get_units_by_resort(session['resort_id'])
    form.unit_id.choices = [(r.id, r.display_name) for r in units]

    if form.validate_on_submit():
        data = request.form.to_dict(flat=True)
        data.pop("csrf_token", None)
        # populate unit_name from unit_id
        print model.Unit.query.get(data['unit_id'])
        data['unit_name'] = model.Unit.query.get(data['unit_id']).display_name
        booking = get_model().create(data)
        return redirect(url_for('.view', id=booking['id']))

    return render_template('form.html', action="add", form=form)


@bookings_api.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    booking = get_model().read(id)

    # if request.method == 'POST':
    #     data = request.form.to_dict(flat=True)
    #
    #     booking = get_model().update(data, id)
    #
    #     return redirect(url_for('.view', id=booking['id']))

    form = forms.BookingForm(obj=booking)
    units = model.get_units_by_resort(session['resort_id'])
    form.unit_id.choices = [(r.id, r.display_name) for r in units]

    # pre-populate form with booking data
    form.unit_id.default = booking['unit_id']
    form.begin_on.data = booking['begin_on']
    form.end_on.data = booking['end_on']
    form.first_name.data = booking['first_name']
    form.last_name.data = booking['last_name']
    form.email.data = booking['email']

    if form.validate_on_submit():
        data = request.form.to_dict(flat=True)
        data.pop("csrf_token", None)
        # populate unit_name from unit_id
        print model.Unit.query.get(data['unit_id'])
        data['unit_name'] = model.Unit.query.get(data['unit_id']).display_name
        booking = get_model().update(data, id)
        return redirect(url_for('.view', id=booking['id']))

    return render_template("form.html", action="edit", booking=booking, form=form)


@bookings_api.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))


# TODO - determine which resort from login
@bookings_api.route('/edit-calendar/<resort_id>')
def edit_calendar(resort_id):
    return render_template("edit_calendar.html", resort_id=resort_id)


# Not Used
# @bookings_api.route("/resorts")
# def get_resort():
#     resorts = model.list_resorts()
#     for resort in resorts:
#         print resort.id, resort.name
#     return "OK"


# Not Used
# @bookings_api.route("/resorts/<id>/unitgroups")
# def get_unitgroups(id):
#     results = model.list_unitgroups(id)
#     return jsonify(results=results)


@bookings_api.route("/resorts/<id>/units")
def get_units(id):
    results = model.get_units_by_resort(id)
    data = [serialize_unit(r) for r in results]
    return jsonify(data=data)


# input datestr is iso format string
@bookings_api.route("/calendar/<datestr>")
def get_calendar_date(datestr):
    date = datetime.strptime(datestr, "%Y-%m-%d")
    calendar = model.get_calendar_date(date)
    # TODO - handle 400
    if not calendar:
        return "400"

    return jsonify(data=serialize_calendar_date(calendar.date_))


# input datestr is iso format string
# begin and end
@bookings_api.route("/calendar")
def get_calendar_dates():
    begin_date = request.args.get('begin')
    end_date = request.args.get('end')
    begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
    if not end_date:
        end_date = begin_date + timedelta(days=DEFAULT_NEXT_DAYS - 1)
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    return get_calendar_date_range(begin_date, end_date)


# input date is date
def get_calendar_date_range(begin_date, end_date):
    dates = model.get_calendar_dates(begin_date, end_date)

    data = [serialize_calendar_date(r.date_) for r in dates]
    return jsonify(data=data)


# Return JSON
# Sample data: http://localhost:8080/bookings/availability/unit/10?begin=2016-07-01&end=2016-07-10
@bookings_api.route("/availability/unit/<id>")
def get_availabilities(id):
    begin_date = request.args.get('begin')
    end_date = request.args.get('end')
    if not begin_date:
        begin_date = '2016-07-01'
    begin_date = datetime.strptime(begin_date, "%Y-%m-%d")

    if not end_date:
        end_date = begin_date + timedelta(days=DEFAULT_NEXT_DAYS - 1)
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    results = model.get_availabilities(id, begin_date, end_date)
    data = [serialize_availability(r) for r in results]
    return jsonify(data=data)


@bookings_api.route('/availability/<id>', methods=['POST'])
def update_availability(id):
    input = json.loads(request.data)

    # TODO - 400 for invalid id
    avail = model.Availability.query.get(input['id'])
    avail.status = -1 if input['booked'] is True else 1
    avail = model.save_entity(avail)
    logging.info(serialize_availability(avail))

    return jsonify(data=serialize_availability(avail))


def serialize_unit(unit):
    return {
        'id': unit.id,
        'name': unit.name,
        'display_name': unit.display_name,
        'unitgroup_id': unit.unitgroup_id
    }


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


def serialize_calendar_date(calendar_date):
    return {
        'year': calendar_date.year,
        'month': calendar_date.month,
        'day': calendar_date.day,
        'weekday': calendar_date.weekday(), # Monday is 0 and Sunday is 6
        'isodate': calendar_date.isoformat()
    }
