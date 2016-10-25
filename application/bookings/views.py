import flask
import json
import logging
from . import get_model, get_content_model
from . import model, forms

from flask import current_app, Blueprint, session, redirect, render_template, request, url_for, flash
from flask import jsonify, json
from functools import wraps
from application.common import utils
from urllib import urlencode
from jinja2 import BaseLoader, TemplateNotFound

import httplib2
import webapp2
import stripe


# Set your secret key: remember to change this to your live secret key in production
# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = "sk_test_BQokikJOvBiI2HlWgH4olfQ2"

# MAILGUN_DOMAIN_NAME = 'sandbox9831351ae46f4ed3b48fdefa8e053e40.mailgun.org'
MAILGUN_DOMAIN_NAME = 'gokitebaja.com'
MAILGUN_API_KEY = 'key-3b38025c106d8d620b501aaf7e89961c'

EMAIL_TEMPLATE = "email/booking_request.html"
EMAIL_SUBJECT_REQUEST = "Your Booking Request has been received"
EMAIL_SUBJECT_CONFIRM = "Confirmation for Your Booking Request"
EMAIL_SUBJECT_DECLINE = "Response for Your Booking Request"
RESPONSE_CONFIRM = "confirm"
RESPONSE_DECLINE = "decline"

RESORTS = ['admin', 'bajajoe', 'captainkirk', 'downwinder', 'kurtnmarina', 'palapas', 'pelican', 'vparaiso', 'ventanabay', 'ventanawind']

bookings_api = Blueprint('bookings', __name__, template_folder='templates')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if g.user is None:
        if not is_loggied_in():
            return redirect(url_for('.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@bookings_api.before_request
def before_request():
    model.ping_mysql()


@bookings_api.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@bookings_api.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            session['logged_in'] = True
            # admin login
            if request.form['username'] == 'admin':
                session['is_admin'] = True
                return redirect(url_for(".list_inbox"))
            # resort login
            session['resort_id'] = get_resort_id_by_username(request.form['username'])
            resort = model.Resort.query.get(session['resort_id'])
            session['resort_name'] = resort.name
            session['nickname'] = resort.display_name
            return redirect(url_for(".list_inbox"))
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)


@bookings_api.route('/logout')
def logout():
    error = None
    if session.get('logged_in'):
        session.pop('logged_in', None)
    if session.get('is_admin'):
        session.pop('is_admin', None)
    if session.get('resort_id'):
        session.pop('resort_id', None)
    if session.get('resort_name'):
        session.pop('resort_name', None)
    if session.get('nickname'):
        session.pop('nickname', None)
    return render_template('login.html', error=error, action="logout")


def valid_login(username, password):
    if username == 'admin' and password == 'admin':
        return True
    if username in RESORTS and password == username:
        return True
    return False
    # user = model.User.query.filter(username=username).first()
    # if user.password == password:
    #     return True


def is_loggied_in():
    if session.get('logged_in'):
        if session['logged_in']:
            return True
    return False


def is_admin():
    if session.get('is_admin'):
        return session['is_admin']


# TODO - save in db
def get_resort_id_by_username(username):
    return RESORTS.index(username)


def get_session_resort_name():
    if session.get('resort_name'):
        return session['resort_name']
    return None


def get_session_nickname():
    if session.get('nickname'):
        return session['nickname']
    return None


def get_session_resort_id():
    if session.get('resort_id'):
        return session['resort_id']
    return None


# @bookings_api.errorhandler(Exception)
# def unhandled_exception(e):
#     logging.error("############# ERROR ###############")
#     logging.error(unicode(e))
#     return render_template('500.html', msg=unicode(e)), 500


@bookings_api.route("/inbox")
@login_required
def list_inbox():
    # token = request.args.get('page_token', None)
    # if token:
    #     token = token.encode('utf-8')

    resort_id = get_session_resort_id()

    if is_admin():
        results = model.list_booking_request_all(model.BOOKING_STATUS_REQUESTED)
        results_confirms = model.list_booking_request_all(model.BOOKING_STATUS_CONFIRMED, 5)
        results_declines = model.list_booking_request_all(model.BOOKING_STATUS_DECLINED, 5)
    else:
        results = model.list_booking_request(model.BOOKING_STATUS_REQUESTED, resort_id)
        results_confirms = model.list_booking_request(model.BOOKING_STATUS_CONFIRMED, resort_id, 5)
        results_declines = model.list_booking_request(model.BOOKING_STATUS_DECLINED, resort_id, 5)

    request_info_list = []
    for result in results:
        request_info = model.BookingRequestInfo(result.BookingRequest, result.Unitgroup)
        request_info_list.append(request_info)

    confirm_info_list = []
    for result in results_confirms:
        request_info = model.BookingRequestInfo(result.BookingRequest, result.Unitgroup)
        confirm_info_list.append(request_info)

    decline_info_list = []
    for result in results_declines:
        request_info = model.BookingRequestInfo(result.BookingRequest, result.Unitgroup)
        decline_info_list.append(request_info)

    # nickname = get_session_nickname()

    try: return render_template(
        "booking-request/landing.html",
        requests=request_info_list,
        confirms=confirm_info_list,
        declines=decline_info_list,
        nickname=get_session_nickname()
    )
    except TemplateNotFound:
        abort(404)


@bookings_api.route("/confirms")
# @login_required
def list_confirms():
    resort_id = get_session_resort_id()
    if is_admin():
        results = model.list_booking_request_all(model.BOOKING_STATUS_CONFIRMED, 100)
    else:
        results = model.list_booking_request(model.BOOKING_STATUS_CONFIRMED, resort_id, 100)

    request_info_list = []
    for result in results:
        request_info = model.BookingRequestInfo(result.BookingRequest, result.Unitgroup)
        request_info_list.append(request_info)

    try: return render_template(
        "booking-request/list_confirms.html",
        confirms=request_info_list,
        nickname=get_session_nickname())
    except TemplateNotFound:
        abort(404)


@bookings_api.route("/declines")
# @login_required
def list_declines():
    resort_id = get_session_resort_id()
    if is_admin():
        results = model.list_booking_request(model.BOOKING_STATUS_DECLINED, resort_id, 5)
    else:
        results = model.list_booking_request(model.BOOKING_STATUS_DECLINED, resort_id, 100)

    request_info_list = []
    for result in results:
        request_info = model.BookingRequestInfo(result.BookingRequest, result.Unitgroup)
        request_info_list.append(request_info)

    try: return render_template(
        "booking-request/list_declines.html",
        declines=request_info_list,
        nickname=get_session_nickname())
    except TemplateNotFound:
        abort(404)


@bookings_api.route("/")
@login_required
def list_bookings():

    booking_info_list = []

    if is_admin():
        results = model.list_bookings_all()
    else:
        # create BookingInfo (dto) from Booking and Unit which has meta data
        resort_id = get_session_resort_id()
        results = model.list_bookings(resort_id)

    for result in results:
        booking_info = model.BookingInfo(result.Booking, result.Unit)
        booking_info_list.append(booking_info)

    try: return render_template(
        "booking/landing.html",
        booking_info_list=booking_info_list, nickname=get_session_nickname())
    except TemplateNotFound:
        abort(404)


@bookings_api.route('/<id>')
# @login_required
def view(id):
    booking = model.Booking.query.get(id)
    unit = model.Unit.query.filter(model.Unit.id == booking.unit_id).one()

    return render_template("booking/view.html", booking=booking, unit=unit)


@bookings_api.route('/<id>/<action>')
# @login_required
def view_confirm(id, action):
    booking = model.Booking.query.get(id)
    unit = model.Unit.query.filter(model.Unit.id == booking.unit_id).one()

    return render_template("booking/view.html", booking=booking, unit=unit, action=action)


# this returns just body w/o menu
@bookings_api.route('/<id>/partial')
# @login_required
def view_booking_modal(id):
    booking = model.Booking.query.get(id)
    unit = model.Unit.query.filter(model.Unit.id == booking.unit_id).one()

    return render_template("booking/view_partial.html", booking=booking, unit=unit)


@bookings_api.route('/<id>/edit', methods=['GET', 'POST'])
# @login_required
def edit(id):
    data = request.form.to_dict(flat=True)
    booking = model.Booking.query.get(id)
    if booking.unit_id:
        unit = model.Unit.query.filter(model.Unit.id == booking.unit_id).one()

    if request.method == 'POST':
        logging.info("[Update] Booking Begin: booking id = %r", id)
        logging.info(data)
        booking = model.update(data, id)
        logging.info("[Update] Booking Success: booking id = %r", id)
        return redirect(url_for('.view_confirm', id=booking['id'], action="Edit"))

    return render_template("booking/form_add.html", action="Edit", booking=booking, unit=unit)


@bookings_api.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    resort_id = get_session_resort_id()
    if not resort_id:
        return redirect(url_for('.login', next=request.url))

    units = model.get_units_by_resort(resort_id)
    booking = None

    booking_request_id = request.args.get('bookingRequestId')

    if booking_request_id:
        booking = build_booking_from_booking_request(booking_request_id)
        # booking.booking_request_id = booking_request_id

        # for dropdown: re-populate units from given unitgroup
        booking_request = get_model().BookingRequest.query.get(booking_request_id)
        units = model.get_units_by_group(booking_request.unitgroup_id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        unit_name = data['unit_name']
        checkin = utils.convert_string_to_date(data['begin_on'])
        checkout = utils.convert_string_to_date(data['end_on'])
        unit = model.Unit.query.filter(model.Unit.name == unit_name).one()

        if not model.is_unit_available(unit.id, checkin, checkout):
            return render_template("500.html", msg="Please check the availability and try again. The Unit is NOT available at least for a day.")

        logging.info("[Create] Booking Begin: unit name = %s, email = %s", unit.name, data['email'])

        # build object
        unit_info = build_unit_info(unit.unitgroup_name, checkin, checkout)
        booking = model.Booking(unit.id, unit.name, unit_info)
        booking.email = data['email']
        booking.first_name = data['first_name']
        booking.last_name = data['last_name']
        booking.guests = data['guests']
        booking.notes = data['notes']

        # set booking_request_id only if exists
        # if data['booking_request_id']:
        #     booking.booking_request_id = data['booking_request_id']

        booking = model.create_booking(booking)
        booking = model.Booking.query.get(booking['id'])

        # send email confirmation if a BookingRequest is associated
        if data['booking_request_id']:
            confirm(data['booking_request_id'], unit_info)

        # return redirect(url_for('.view_confirm', id=booking['id'], action="Add"))
        return redirect(url_for('.view_confirm', id=booking.id, action="Add"))

    return render_template("booking/form_add.html", action="Add", units=units, booking=booking, booking_request_id=booking_request_id )


# def build_booking_info(booking):
#     unit = model.Unit.query.get(booking.unit_id)
#     unit_info = build_unit_info(unit.unitgroup_name, booking.begin_on, booking.end_on)
#     booking_info = model.BookingInfo(booking.begin_on, booking.end_on, booking.guests, booking.id, unit_info)
#     booking_info.avg_price = unit_info.avg_price
#     booking_info.nights = unit_info.nights
#     booking_info.first_name = booking.first_name
#     booking_info.last_name = booking.last_name
#     booking_info.email = booking.email
#
#     return booking_info


@bookings_api.route('/<id>/delete')
# @login_required
def delete(id):
    logging.info("[Delete] Booking Begin: booking id = %s", id)
    model.delete(id)
    logging.info("[Delete] Booking Success: booking id = %s", id)
    return redirect(url_for('.list_bookings'))


@bookings_api.route("/calendar")
@login_required
def list_calendar_default():
    begin_date = utils.get_todays_date()
    begin_date = utils.convert_date_to_string(begin_date)

    if is_admin():
        resorts = model.get_resorts()
        return render_template("calendar/admin.html", resorts=resorts, nickname=get_session_nickname())

    # resort = model.Resort.query.get(session['resort_id'])
    resort_name = get_session_resort_name()
    return list_calendar(resort_name, begin_date)


@bookings_api.route("/calendar/<resort_name>")
def list_calendar_by_resort(resort_name):
    begin_date = utils.get_default_begin_date()
    return list_calendar(resort_name, utils.convert_date_to_string(begin_date))


@bookings_api.route("/calendar/<resort_name>/<begin_date>")
# @login_required
def list_calendar(resort_name, begin_date):
    begin_date = utils.convert_string_to_date(begin_date)
    # end_date = utils.get_end_date_from_begin_date(begin_date, utils.TWO_WEEKS)

    if request.args.get('prev'):
        # rewind two weeks
        begin_date = utils.get_end_date_from_begin_date(begin_date, utils.TWO_WEEKS_BEFORE)

    elif request.args.get('next'):
        # forward two weeks
        begin_date = utils.get_end_date_from_begin_date(begin_date, utils.TWO_WEEKS)
    else:
        # current date
        pass

    end_date = utils.get_end_date_from_begin_date(begin_date, utils.TWO_WEEKS)

    resort = model.get_resort_by_name(resort_name)
    if not resort:
        return render_template("500.html", msg="Page does not exist.")

    units = get_calendar(resort_name, begin_date, end_date)
    results = model.get_bookings(resort.id, begin_date, end_date)

    booking_info_list = []
    for result in results:
        booking_info = model.BookingInfo(result.Booking, result.Unit)
        booking_info_list.append(booking_info)

    return render_template("calendar/landing.html", units=units, booking_info_list=booking_info_list, nickname=get_session_nickname())


@bookings_api.route('/calendar/edit', methods=['GET', 'POST'])
# @login_required
def edit_availability():
    if not request.form:
        return 'Empty Data', 400

    avail_id = request.form['avail_id']
    unit_id = request.form['unit_id']
    date_slot = request.form['date_slot']
    status = request.form['status']
    avail = model.get_availability(unit_id, date_slot)

    # this is like 'toggle'
    if not avail:
        logging.info("<Calendar> [Create] Availability Begin")
        avail = model.Availability(unit_id, date_slot, 2)
        avail = model.save_entity(avail)
        logging.info("<Calendar> [Create] Availability (Status = %d) Success", status)
    else:
        logging.info("<Calendar> [Delete] Availability Begin")
        avail = model.Availability.query.get(avail.id)
        model.delete_entity(avail)
        # availability record is deleted but need to set status = 0 (available) so UI can re-render the result
        avail.status = 0
        logging.info("<Calendar> [Delete] Availability (id = %r) Success", id)

    logging.info(serialize_availability(avail))
    return jsonify(data=serialize_availability(avail))


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


@bookings_api.route("/calendar/resort/<name>")
def get_calendar(name):

    begin_date = utils.get_begin_date(request)
    end_date = utils.get_end_date(request, utils.TWO_WEEKS)
    data = get_calendar(name, begin_date, end_date)
    return jsonify(results=data)


def get_calendar(resort_name, begin_date, end_date):
    units = model.get_units_by_resort_name(resort_name)
    data = []
    for unit in units:
        results = model.get_availabilities(unit.id, begin_date, end_date)
        # sample result : (datetime.date(2016, 10, 11), 12, 1, 62, 31)
        status_info_list = []
        for result in results:
            date_ = result[0]
            unit_id = result[1]
            status = result[2]
            availability_id = result[3]
            booking_id = result[4]
            status_info = get_content_model().StatusInfo(unit, date_, status, unit_id, availability_id, booking_id)
            status_info_list.append(status_info)

        calendar_info = get_content_model().CalendarInfo(unit, resort_name, status_info_list)
        data.append(calendar_info.serialize_calendar_info())

    return data


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

    if not request.form:
        return 'Empty Data', 400

    checkin = request.form['from']
    checkout = request.form['to']
    guests = request.form['guests']
    email = request.form['email']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    stripe_token = request.form['stripe_token']
    print "*****"
    print stripe_token

    customer_id = create_stripe_customer(stripe_token, email)

    # TODO - save customer_id to database

    # TODO - charge later
    charge_customer(customer_id, 150)

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

    return send_booking_mail(booking_request, None, "")
    #return jsonify(results=get_model().BookingRequest.serialize_booking_request(booking_request))


# Now called from "Create Booking" flow.
# No comment will be added for /bo email
# @bookings_api.route('/confirm', methods=['POST'])
def confirm(booking_request_id, unit_info):

    # booking_request = build_booking_request(id)
    # logging.info(booking_request)
    booking_request = model.BookingRequest.query.get(booking_request_id)
    if booking_request:
        booking_request.status = model.BOOKING_STATUS_CONFIRMED
        booking_request = model.save_entity(booking_request)
        booking_request.unit_info = unit_info
        logging.info("[CONFIRM Booking Request] : id = %d, unitgroup = %s, email = %s", booking_request.id, booking_request.unitgroup_name, booking_request.email)

        return send_booking_mail(booking_request, RESPONSE_CONFIRM, "")
    pass

# Comment will be added for decline email
@bookings_api.route('/decline', methods=['POST'])
def decline():
    id = request.form['bookingRequestId']
    if not id:
        return 'Sorry, Invalid Request. bookingRequestId is required', 400
    comment = request.form['comment']

    booking_request = get_model().BookingRequest.query.get(id)
    booking_request.status = model.BOOKING_STATUS_DECLINED
    booking_request = model.save_entity(booking_request)

    logging.info("sending DECLINE email : id = %d, name = %s", booking_request.id, booking_request.unitgroup_name)
    unit_info = build_unit_info_from_booking_request(booking_request)

    booking_request.unit_info = unit_info
    return send_booking_mail(booking_request, RESPONSE_DECLINE, comment)
    #return redirect(url_for('.list_inbox'))


@bookings_api.route('/mail/<groupname>', methods=['POST'])
def test_mail(groupname):
    input = json.loads(request.data)
    if not input:
        return 'Sorry, Invalid Request', 400

    resort_email = input['recipient']
    # booking request sample data
    checkin = "2016-11-01"
    checkout = "2016-11-05"
    guests = 2
    email = "gokitebaja@gmail.com"

    checkin = utils.convert_string_to_date(checkin)
    checkout = utils.convert_string_to_date(checkout)

    unitgroup = get_content_model().find_unit_by_name(groupname)
    if not unitgroup:
        return 'Sorry, Invalid Unitgroup Name', 400

    unit_info = get_content_model().UnitInfo(unitgroup, checkin, checkout)
    booking_request = get_model().BookingRequest(groupname, 1, checkin, checkout, guests, email, unit_info)
    booking_request.first_name = "Frodo"
    booking_request.last_name = "Baggins"

    email_content = send_mail(resort_email, booking_request, None, "")
    # email_content = send_mail(resort_email, booking_request, RESPONSE_CONFIRM, "")
    # email_content = send_mail(resort_email, booking_request, RESPONSE_DECLINE, "We have availability after Jan 4th, 2016.")
    return email_content


# build booking instance from BookingRequest. Unit is not determined yet at this time
def build_booking_from_booking_request(booking_request_id):

    booking_request = get_model().BookingRequest.query.get(booking_request_id)
    unit_info = build_unit_info_from_booking_request(booking_request)

    # build Booking instance from BookingRequest
    booking = model.Booking(None, None, unit_info)
    booking.email = booking_request.email
    booking.first_name = booking_request.first_name
    booking.last_name = booking_request.last_name

    return booking


def get_first_available_unit(unitgroup_id, checkin, checkout):
    units = model.get_units_by_group(unitgroup_id)
    for unit in units:
        if model.is_unit_available(unit.id, checkin, checkout):
            return unit
    return None


def build_unit_info_from_booking_request(booking_request):
    # booking_request = get_model().BookingRequest.query.get(id)
    # booking_request.unit_info = build_unit_info(booking_request.unitgroup_name, booking_request.checkin, booking_request.checkout)
    # return booking_request
    return build_unit_info(booking_request.unitgroup_name, booking_request.checkin, booking_request.checkout)


def build_unit_info(unitgroup_name, checkin, checkout):
    checkin = utils.convert_string_to_date(utils.convert_date_to_string(checkin))
    checkout = utils.convert_string_to_date(utils.convert_date_to_string(checkout))
    unitgroup = get_content_model().find_unit_by_name(unitgroup_name)
    return get_content_model().UnitInfo(unitgroup, checkin, checkout)

# checkin and checkout is date
# def get_unit_info(groupname, checkin, checkout):
#     # checkin = utils.convert_date_to_string(utils.convert_string_to_date(checkin))
#     # checkout = utils.convert_date_to_string(utils.convert_string_to_date(checkout))
#     unitgroup = get_content_model().find_unit_by_name(groupname)
#     unit_info = get_content_model().UnitInfo(unitgroup, checkin, checkout)
#     logging.info(checkin)
#     logging.info("Retrieving UnitInfo.... %r %r %r", groupname, checkin, checkout)
#     logging.info(unit_info)

    return unit_info


# wrapper to find resort email address
def send_booking_mail(booking_request, response_type, comment):
    resort_email = get_resort_email_from_unitgroup(booking_request.unitgroup_id)
    return send_mail(resort_email, booking_request, response_type, comment)


# get resort email (email will be added to DB in the future)
def get_resort_email_from_unitgroup(unitgroup_id):
    resort = model.get_resort_by_unitgroup_id(unitgroup_id)
    resort_info = get_content_model().find_resort_by_name(resort.name)
    return resort_info.email


def send_mail(resort_email, booking_request, response_type, comment):
    subject = "Thank you!"

    if response_type == RESPONSE_CONFIRM:
        if booking_request.first_name:
            subject = "Thank you " + booking_request.first_name + "!"
        status = "Your booking request has been confirmed by the resort."
        comment = "If you have any question regarding this confirmation, please contact the resort directly at " + resort_email
        email_data = get_model().EmailData(booking_request, subject, status, comment)
        customer_email = email_data.booking_request.email
        email_content = send_complex_message(resort_email, customer_email, email_data, EMAIL_SUBJECT_CONFIRM)
    elif response_type == RESPONSE_DECLINE:
        subject = "Sorry, the unit you requested is not available on those dates..."
        status = "For further assistance, please contact the resort directly at " + resort_email
        email_data = get_model().EmailData(booking_request, subject, status, comment)
        customer_email = email_data.booking_request.email
        email_content = send_complex_message(resort_email, customer_email, email_data, EMAIL_SUBJECT_DECLINE)
    else:
        subject = "Thank you " + booking_request.first_name + "!"
        status = "Your booking request has been sent to the resort at " + resort_email
        email_data = get_model().EmailData(booking_request, subject, status, comment)
        customer_email = email_data.booking_request.email
        email_content = send_complex_message(resort_email, customer_email, email_data, EMAIL_SUBJECT_REQUEST)
    return jsonify(results=email_content)


# def send_inquiry_mail(recipient, comment):
#     # TODO get recipient from content API (email for resort)
#     recipient = 'book@gokitebaja.com'
#     subject = "Thank you!"
#     email_content = send_complex_message(recipient, email_data, EMAIL_SUBJECT_DECLINE)
#     return jsonify(results=email_content)


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


def send_complex_message(resort_email, customer_email, email_data, email_subject):
    http = httplib2.Http()
    http.add_credentials('api', MAILGUN_API_KEY)
    html_body = render_template(EMAIL_TEMPLATE,
                                email_data=email_data)

    url = 'https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN_NAME)
    data = {
        # 'from': 'GoKiteBaja <mailgun@{}>'.format(MAILGUN_DOMAIN_NAME),
        'from': 'GoKiteBaja <book@{}>'.format(MAILGUN_DOMAIN_NAME),
        'to': customer_email,
        'cc': resort_email,
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


def create_stripe_customer(stripe_token, email):
    logging.info("[Stripe : Create Customer]")
    customer = stripe.Customer.create(
        email=email,
        source=stripe_token,
        description="Test customer"
    )
    logging.info(customer)
    return customer.id


def charge_customer(customer_id, amount):
    logging.info("[Stripe : Charge]")
    charge = stripe.Charge.create(
        customer=customer_id,
        amount=amount,
        currency='usd',
        description='Test Charge'
    )
    logging.info(charge)
    return charge


