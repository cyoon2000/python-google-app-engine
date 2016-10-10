import flask
import json
import logging
from . import get_model, get_content_model
from . import model, forms

from flask import current_app, Blueprint, session, redirect, render_template, request, url_for, flash
from flask import jsonify, json
from flask_wtf import Form
from application.common import utils

from urllib import urlencode

import httplib2
import webapp2

# MAILGUN_DOMAIN_NAME = 'sandbox9831351ae46f4ed3b48fdefa8e053e40.mailgun.org'
MAILGUN_DOMAIN_NAME = 'gokitebaja.com'
MAILGUN_API_KEY = 'key-3b38025c106d8d620b501aaf7e89961c'

EMAIL_TEMPLATE = "email/booking_request.html"
EMAIL_SUBJECT_REQUEST = "Your Booking Request has been received"
EMAIL_SUBJECT_CONFIRM = "Confirmation for Your Booking Request"
EMAIL_SUBJECT_DECLINE = "Response for Your Booking Request"
RESPONSE_CONFIRM = "confirm"
RESPONSE_DECLINE = "decline"

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


@bookings_api.errorhandler(Exception)
def unhandled_exception(e):
    logging.error('Exception: %s', unicode(e))
    return render_template('500.html', msg=unicode(e)), 500


@bookings_api.route("/requests")
def list_booking_requests():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    requests, next_page_token = get_model().list_booking_request(cursor=token)
    confirms = get_model().list_booking_request_confirmed()
    declines = get_model().list_booking_request_declined()

    try: return render_template(
        "booking-request/list.html",
        requests=requests,
        confirms=confirms,
        declines=declines,
        next_page_token=next_page_token)
    except TemplateNotFound:
        abort(404)


@bookings_api.route("/confirms")
def list_confirms():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    # requests, next_page_token = get_model().list_booking_request(cursor=token)
    confirms = get_model().list_booking_request_confirmed(100)

    try: return render_template(
        "booking-request/list_confirms.html",
        confirms=confirms)
        # confirms=confirms,
        # next_page_token=next_page_token)
    except TemplateNotFound:
        abort(404)


@bookings_api.route("/declines")
def list_declines():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    # requests, next_page_token = get_model().list_booking_request(cursor=token)
    declines = get_model().list_booking_request_declined(100)

    try: return render_template(
        "booking-request/list_declines.html",
        declines=declines)
    # confirms=confirms,
    # next_page_token=next_page_token)
    except TemplateNotFound:
        abort(404)

@bookings_api.route("/")
def list_bookings():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    bookings, next_page_token = model.list_bookings(cursor=token)

    try: return render_template(
        "booking/list.html",
        bookings=bookings,
        next_page_token=next_page_token)
    except TemplateNotFound:
        abort(404)


@bookings_api.route('/<id>')
def view(id):
    booking = get_model().read(id)
    return render_template("booking/view.html", booking=booking)


@bookings_api.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    booking = model.Booking.query.get(id)

    if request.method == 'POST':
        logging.info("[Update] Booking Begin: unit name = %s, email = %s", booking.unit_name, booking.email)
        data = request.form.to_dict(flat=True)
        booking = model.update(data, id)
        logging.info("[Update] Booking Success: booking id = %d", booking['id'])
        return redirect(url_for('.view', id=booking['id']))

    return render_template("booking/form_edit.html", action="Edit", booking=booking)


@bookings_api.route('/add', methods=['GET', 'POST'])
def add():

    units = model.get_units_by_resort(session['resort_id'])

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        unit_name = data['unit_name']
        checkin = utils.convert_string_to_date(data['begin_on'])
        checkout = utils.convert_string_to_date(data['end_on'])
        unit = model.Unit.query.filter(model.Unit.name == unit_name).one()

        if not is_unit_available(unit.id, checkin, checkout):
            return render_template("500.html", msg="Please check the availability and try again. The Unit is NOT available for the dates you specified.")

        logging.info("[Create] Booking Begin: unit name = %s, email = %s", unit.name, data['email'])
        unit_info = get_unit_info(unit.unitgroup_name, checkin, checkout)
        booking = model.Booking(unit.id, unit.name, unit_info)
        booking.email = data['email']
        booking.first_name = data['first_name']
        booking.last_name = data['last_name']
        booking.guests = data['guests']
        booking.notes = data['notes']
        booking = model.create_booking(booking)

        logging.info("[Create] Booking Success: booking id = %d, unit name = %s, email = %s", booking['id'], unit.name, data['email'])
        return redirect(url_for('.view', id=booking['id']))

    return render_template("booking/form_add.html", action="Add", units=units, booking={})


@bookings_api.route('/<id>/delete')
def delete(id):
    logging.info("[Delete] Booking Begin: booking id = %s", id)
    model.delete(id)
    logging.info("[Delete] Booking Success: booking id = %s", id)
    return redirect(url_for('.list_bookings'))


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
        calendar_info = get_content_model().CalendarInfo(unit, name, date_list, status_list)
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
    guests = request.args.get('guests')
    if not guests:
        guests = 2

    # 'search' returns availability by unit groups (id, name, count(available # of units))
    search_results = model.search_by_resort(resortname, begin_date, end_date)

    # build unit_info_list from 'search' result
    unit_info_list = []
    for result in search_results:
        unit = get_content_model().find_unit_by_name(result.name)
        unit_info = get_content_model().UnitInfo(unit, begin_date, end_date, guests, int(float(result.available)))
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
    guests = request.args.get('guests')
    if not guests:
        guests = 2

    unit = get_content_model().find_unit_by_name(typename)
    if not unit:
        return 'Sorry, Invalid Request', 400

    # TODO - check availability again
    unit_info = get_content_model().UnitInfo(unit, begin_date, end_date, guests)
    results = unit_info.serialize_unit_detail()
    return jsonify(results=results)


@bookings_api.route('/book/<groupname>', methods=['POST'])
def book(groupname):

    # input = request.get_json()
    # input = request.get_data()
    # if not input:
    #     return 'Empty Data', 400
    # checkin = input['checkin']
    # checkout = input['checkout']
    # guests = input['guests']

    checkin = request.args.get('from')
    checkout = request.args.get('to')
    guests = request.args.get('guests')
    email = request.args.get('email')
    firstname = request.args.get('firstname')
    lastname = request.args.get('lastname')

    checkin = utils.convert_string_to_date(checkin)
    checkout = utils.convert_string_to_date(checkout)

    results = get_model().search_by_unit_group(groupname, checkin, checkout)
    for result in results:
        count = result[2]
        if not count > 0:
            return 'Sorry, those dates you requested are not available', 400

        unitgroup_id = result[0]
        unitgroup = get_content_model().find_unit_by_name(groupname)
        unit_info = get_content_model().UnitInfo(unitgroup, checkin, checkout)
        booking_request = get_model().BookingRequest(groupname, unitgroup_id, checkin, checkout, guests, email, unit_info)
        booking_request.first_name = firstname
        booking_request.last_name = lastname
        booking_request = model.save_entity(booking_request)
        logging.info(get_model().BookingRequest.serialize_booking_request(booking_request))

    return send_mail(booking_request, None, "")
    #return jsonify(results=get_model().BookingRequest.serialize_booking_request(booking_request))


# No comment will be added for confirm email
@bookings_api.route('/confirm', methods=['POST'])
def confirm():
    id = request.form['bookingRequestId']
    if not id:
        return 'Sorry, Invalid Request. bookingRequestId is required', 400

    booking_request = build_booking_request_for_email(id)

    #
    # FEATURE - "Automatic Booking' - HOLD OFF for now
    #
    # create booking record from booking request, assign a unit.
    # logging.info("CONFIRMATION Begin: id = %d, unitgroup = %s, email = %s", booking_request.id, booking_request.unitgroup_name, booking_request.email)
    # unit = get_first_available_unit(booking_request.unitgroup_id, booking_request.checkin, booking_request.checkout)
    # logging.info("[first available unit] unit id = %d unit name = %s", unit.id, unit.name)
    # if unit:
    #     booking = build_booking_from_booking_request(unit, booking_request)
    #     return model.create_entity(booking)
    #     if not booking:
    #         raise RuntimeError(
    #         'BookingRequest Confirmation error. No available unit : {} {}'.format(booking_request.id, booking_request.email))

    booking_request.status = "CONFIRMED"
    booking_request = model.save_entity(booking_request)

    logging.info("CONFIRMATION Success: id = %d, unitgroup = %s, email = %s", booking_request.id, booking_request.unitgroup_name, booking_request.email)

    return send_mail(booking_request, RESPONSE_CONFIRM, "")


# Comment will be added for decline email
@bookings_api.route('/decline', methods=['POST'])
def decline():
    id = request.form['bookingRequestId']
    if not id:
        return 'Sorry, Invalid Request. bookingRequestId is required', 400
    comment = request.form['comment']

    booking_request = build_booking_request_for_email(id)
    booking_request.status = "DECLINED"
    booking_request = model.save_entity(booking_request)

    logging.info("sending DECLINE email : id = %d, name = %s", booking_request.id, booking_request.unitgroup_name)
    return send_mail(booking_request, RESPONSE_DECLINE, comment)


@bookings_api.route('/mail/<groupname>', methods=['POST'])
def test_mail(groupname):
    input = json.loads(request.data)
    if not input:
        return 'Sorry, Invalid Request', 400

    recipient = input['recipient']
    checkin = "2016-11-01"
    checkout = "2016-11-05"
    guests = 2
    email = "cherieyoun@gmail.com"

    checkin = utils.convert_string_to_date(checkin)
    checkout = utils.convert_string_to_date(checkout)

    unitgroup = get_content_model().find_unit_by_name(groupname)
    if not unitgroup:
        return 'Sorry, Invalid Unitgroup Name', 400

    unit_info = get_content_model().UnitInfo(unitgroup, checkin, checkout)
    booking_request = get_model().BookingRequest(groupname, 1, checkin, checkout, guests, email, unit_info)
    booking_request.first_name = "Frodo"
    booking_request.last_name = "Baggins"

    email_content = send_mail(booking_request, None, "")
    #email_content = send_mail(booking_request, RESPONSE_CONFIRM, "")
    #email_content = send_mail(booking_request, RESPONSE_DECLINE, "We have availability after Jan 4th, 2016.")
    return email_content

# checkin and checkout is date
def get_unit_info(groupname, checkin, checkout):
    # checkin = utils.convert_string_to_date(checkin)
    # checkout = utils.convert_string_to_date(checkout)
    unitgroup = get_content_model().find_unit_by_name(groupname)
    unit_info = get_content_model().UnitInfo(unitgroup, checkin, checkout)
    return unit_info


def is_unit_available(unit_id, checkin, checkout):
    results = model.get_availabilities(unit_id, checkin, checkout)
    results_by_unit = zip(*results)
    # extract status field from result set
    status_list = results_by_unit[2]
    print status_list
    print sum(status_list)
    if sum(status_list) > 0:
        return False
    return True


def build_booking_from_booking_request(unit, booking_request):
    # checkin = utils.convert_date_to_string(booking_request.checkin)
    # checkout = utils.convert_date_to_string(booking_request.checkout)
    unit_info = get_unit_info(booking_request.unitgroup_name, booking_request.checkin, booking_request.checkout)
    booking = model.Booking(unit.id, unit.name, unit_info)
    booking.email = booking_request.email
    booking.first_name = booking_request.first_name
    booking.last_name = booking_request.last_name

    return booking


def get_first_available_unit(unitgroup_id, checkin, checkout):
    units = model.get_units_by_group(unitgroup_id)
    for unit in units:
        if is_unit_available(unit.id, checkin, checkout):
            return unit
    return None


def build_booking_request_for_email(id):
    booking_request = get_model().BookingRequest.query.get(id)

    checkin = utils.convert_string_to_date(utils.convert_date_to_string(booking_request.checkin))
    checkout = utils.convert_string_to_date(utils.convert_date_to_string(booking_request.checkout))
    unitgroup = get_content_model().find_unit_by_name(booking_request.unitgroup_name)
    unit_info = get_content_model().UnitInfo(unitgroup, checkin, checkout)
    booking_request.unit_info = unit_info
    return booking_request


def send_mail(booking_request, response_type, comment):
    # TODO get recipient from content API (email for resort)
    recipient = 'book@gokitebaja.com'

    if response_type == RESPONSE_CONFIRM:
        subject = "Thank you " + booking_request.first_name + "!"
        status = "Your booking request has been confirmed by the resort."
        email_data = get_model().EmailData(booking_request, subject, status, comment)
        email_content = send_complex_message(recipient, email_data, EMAIL_SUBJECT_CONFIRM)
    elif response_type == RESPONSE_DECLINE:
        subject = "Sorry, the unit you requested is not available..."
        status = "Your booking request cannot be accepted by the resort at this time."
        email_data = get_model().EmailData(booking_request, subject, status, comment)
        email_content = send_complex_message(recipient, email_data, EMAIL_SUBJECT_DECLINE)
    else:
        subject = "Thank you " + booking_request.first_name + "!"
        status = "Your booking request has been sent to the resort."
        email_data = get_model().EmailData(booking_request, subject, status, comment)
        email_content = send_complex_message(recipient, email_data, EMAIL_SUBJECT_REQUEST)
    return jsonify(results=email_content)


def send_simple_message(recipient):
    http = httplib2.Http()
    http.add_credentials('api', MAILGUN_API_KEY)

    url = 'https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN_NAME)
    data = {
        'from': 'GoKiteBaja <mailgun@{}>'.format(MAILGUN_DOMAIN_NAME),
        'to': recipient,
        'subject': 'This is an example email from Mailgun',
        'text': 'Test message from Mailgun'
    }

    resp, content = http.request(url, 'POST', urlencode(data))

    if resp.status != 200:
        raise RuntimeError(
            'Mailgun API error: {} {}'.format(resp.status, content))


def send_complex_message(recipient, email_data, email_subject):
    http = httplib2.Http()
    http.add_credentials('api', MAILGUN_API_KEY)
    html_body = render_template(EMAIL_TEMPLATE,
                                email_data=email_data)

    url = 'https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN_NAME)
    data = {
        'from': 'GoKiteBaja <mailgun@{}>'.format(MAILGUN_DOMAIN_NAME),
        'to': email_data.booking_request.email,
        'cc': recipient,
        'bcc': "book@gokitebaja.com",
        'subject': email_subject,
        'text': email_subject,
        'html': html_body
        # 'html': '<html>HTML <strong>version</strong> of the body</html>'
    }

    resp, content = http.request(url, 'POST', urlencode(data))

    if resp.status != 200:
        raise RuntimeError(
            'Mailgun API error: {} {}'.format(resp.status, content))

    return html_body


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
