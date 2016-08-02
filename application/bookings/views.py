import flask
import json
import logging
from . import get_model, get_content_model
from . import model, forms

from flask import current_app, Blueprint, session, redirect, render_template, request, url_for, flash
from flask import jsonify, json
from flask_wtf import Form
from application.common import utils

bookings_api = Blueprint('bookings', __name__, template_folder='templates')

@bookings_api.before_request
def before_request():
    # TODO - save resort_id in session upon login
    session['resort_name'] = 'kirk'
    # resort = model.Resort.query.filter_by(name=session['resort_name']).one()
    resort = model.get_resort_by_name(session['resort_name'])
    session['resort_id'] = resort.id


@bookings_api.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# @bookings_api.before_request
# def before_request2():
#     g.user = None
#     g.resort = None
#     if 'user_id' in session:
#       g.user = model.User.query.get(session['user_id'])


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
        data['unit_name'] = model.Unit.query.get(data['unit_id']).display_name
        booking = get_model().create(data)
        return redirect(url_for('.view', id=booking['id']))

    return render_template('form.html', action="Add", form=form)


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
    form.unit_id.data = booking['unit_id']
    form.begin_on.data = booking['begin_on']
    form.end_on.data = booking['end_on']
    form.first_name.data = booking['first_name']
    form.last_name.data = booking['last_name']
    form.email.data = booking['email']

    if form.validate_on_submit():
        # TODO - FIXME - This does not work
        # form.populate_obj(booking)
        data = request.form.to_dict(flat=True)
        data.pop("csrf_token", None)
        # populate unit_name from unit_id
        data['unit_name'] = model.Unit.query.get(data['unit_id']).display_name
        booking = model.update(data, id)
        return redirect(url_for('.view', id=booking['id']))

    return render_template("form.html", action="Edit", booking=booking, form=form)


@bookings_api.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))


# TODO - add calendar navigation prev/next
@bookings_api.route('/edit-calendar')
def edit_calendar():
    begin_date = utils.get_begin_date(request)
    end_date = utils.get_end_date(request, utils.TWO_WEEKS)

    resort = model.Resort.query.get(session['resort_id'])
    units = model.get_units_by_resort(resort.id)

    dates = model.get_calendar_dates(begin_date, end_date)
    bookings = model.get_bookings(begin_date, end_date)

    return render_template("edit_calendar.html", resort=resort, units=units, dates=dates, bookings=bookings)


@bookings_api.route("/resorts/<id>/units")
def get_units(id):
    results = model.get_units_by_resort(id)
    data = [serialize_unit(r) for r in results]
    return jsonify(data=data)


# input datestr is iso format string
@bookings_api.route("/calendar/<datestr>")
def get_calendar_date(datestr):
    date = utils.convert_string_to_date(datestr)
    calendar = model.get_calendar_date(date)
    # TODO - handle 400
    if not calendar:
        return "400"

    return jsonify(data=serialize_calendar_date(calendar.date_))


# input datestr is iso format string
# begin and end
# @bookings_api.route("/calendar")
# def get_calendar_dates():
#     begin_date = request.args.get('begin')
#     end_date = request.args.get('end')
#
#     begin_date = utils.convert_string_to_date(begin_date)
#     if not end_date:
#         end_date = utils.get_default_end_date(begin_date)
#     else:
#         end_date = utils.convert_string_to_date(end_date)
#
#     return get_calendar_dates(begin_date, end_date)


# input date is date
# def get_calendar_dates(begin_date, end_date):
#     dates = model.get_calendar_dates(begin_date, end_date)
#     data = [serialize_calendar_date(r.date_) for r in dates]
#     return jsonify(data=data)


# Return JSON
# Sample data: http://localhost:8080/bookings/availability/unit/10?from=2016-07-01&to=2016-07-10
@bookings_api.route("/availability/unit/<id>")
def get_availabilities(id):

    begin_date = utils.get_begin_date(request)
    end_date = utils.get_end_date(request, utils.TWO_WEEKS)

    results = model.get_availabilities(id, begin_date, end_date)
    data = [serialize_availability(r) for r in results]
    return jsonify(data=data)


@bookings_api.route('/availability/<unit_id>', methods=['POST'])
def update_availability(unit_id):
    input = json.loads(request.data)
    if input['id']:
        avail = model.Availability.query.get(input['id'])
        avail = model.delete_entity(avail)

    else:
        #avail = model.Availability.query.get(input['id'])
        #avail.status = -1 if input['booked'] is True else 1
        #avail = model.save_entity(avail)
        # 2=blocked
        avail = model.Availability(input['unit_id'], input['date_slot'], 2)
        avail = model.save_entity(avail)
        logging.info(serialize_availability(avail))

    return jsonify(data=serialize_availability(avail))
    # return jsonify(data="Success")


@bookings_api.route("/calendar/resort/<name>")
def get_calendar(name):

    begin_date = utils.get_begin_date(request)
    end_date = utils.get_end_date(request, utils.TWO_WEEKS)

    units = model.get_units_by_resort_name(name)
    date_list = None
    data = []
    for unit in units:
        results = model.get_availabilities(unit.id, begin_date, end_date)
        results_by_unit = zip(*results)
        if not date_list:
            date_list = results_by_unit[0]
        # extract status field from result set
        status_list = results_by_unit[2]
        calendar_info = get_content_model().CalendarInfo(unit, date_list, status_list)
        data.append(calendar_info.serialize_calendar_info())

    return jsonify(results=data)


@bookings_api.route('/search')
def search():
    begin_date = utils.get_begin_date(request)
    end_date = utils.get_end_date(request)
    # guests = request.args.get('guests')

    # 'search' returns availability by resorts (id, name, count(available # of units))
    search_results = model.search(begin_date, end_date)

    # for each resort entity, find/serialize resort content, instantiate ResortInfo
    resort_info_list = []
    for result in search_results:
        resort = get_content_model().find_resort_by_name(result.name)
        resort_info = get_content_model().ResortInfo(resort, begin_date, end_date, result.count)
        resort_info_list.append(resort_info)

    resort_info_list.sort(key=lambda x: (x.active, x.count), reverse=True)
    results = get_content_model().serialize_resort_info_list(resort_info_list)

    return jsonify(results=results)


# /search/resort/bj?from=2016-07-20&to=2016-07-22&guests=1
@bookings_api.route('/search/resort/<resortname>')
def search_resort(resortname):
    begin_date = utils.get_begin_date(request)
    end_date = utils.get_end_date(request)
    # guests = request.args.get('guests')

    # 'search' returns availability by unit groups (id, name, count(available # of units))
    search_results = model.search_by_resort(resortname, begin_date, end_date)

    # build unit_info_list from 'search' result
    unit_info_list = []
    for result in search_results:
        unit = get_content_model().find_unit_by_name(result.name)
        unit_info = get_content_model().UnitInfo(unit, begin_date, end_date, int(float(result.available)))
        unit_info_list.append(unit_info)

    # build ResortInfo
    resort = get_content_model().find_resort_by_name(resortname)
    resort_info = get_content_model().ResortInfo(resort, begin_date, end_date)
    resort_info.set_unit_info_list(unit_info_list)

    results = resort_info.serialize_resort_info()
    return jsonify(results=results)


@bookings_api.route('/search/<resortname>/<typename>')
def search_unit(resortname, typename):

    # begin_date = request.args.get('from')
    # end_date = request.args.get('to')
    begin_date = utils.get_begin_date(request)
    end_date = utils.get_end_date(request)

    unit = get_content_model().find_unit_by_name(typename)
    if not unit:
        return 'Sorry, Invalid Request', 400

    unit_info = get_content_model().UnitInfo(unit, begin_date, end_date)
    results = unit_info.serialize_unit_detail()
    return jsonify(results=results)


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
        'unit_id': availability.unit_id,
        'date_slot': availability.date_slot.isoformat(),
        'month': availability.date_slot.month,
        'day': availability.date_slot.day,
        'weekday': availability.date_slot.weekday(), # Monday is 0 and Sunday is 6
        'booked': False if availability.status == 0 else True,
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
