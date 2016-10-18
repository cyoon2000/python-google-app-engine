import logging
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy import func, or_
from sqlalchemy.sql import text
from database import db
from application.contents.data import read_data_resorts, read_data_units, read_data_unitnames
from application.common import utils

builtin_list = list

BOOKING_STATUS_REQUESTED = 'CREATED'
BOOKING_STATUS_CONFIRMED = 'CONFIRMED'
BOOKING_STATUS_DECLINED = 'DECLINED'

def init_app(app):
    db.init_app(app)


def from_sql(row):
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data


class Base(db.Model):
    __abstract__ = True

    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(64), default=lambda: 'admin')
    updated_by = db.Column(db.String(64), default=lambda: 'admin')


class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # TODO - encrypt later
    # def hash_password(self, password):
    #     self.password_hash = pwd_context.encrypt(password)
    #
    # def verify_password(self, password):
    #     return pwd_context.verify(password, self.password_hash)


class Resort(Base):
    __tablename__ = 'resort'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    display_name = db.Column(db.String(30), nullable=False)
    active = db.Column(db.Boolean, default=True)
    # relationships
    unitgroups = db.relationship("Unitgroup", backref='resort')

    # def __init__(self, name, display_name):
    #     self.name = name
    #     self.display_name = display_name
    # def _init__(self, **kwargs):
    #     self.name = kwargs.pop('name', None)
    #     self.displayName = kwargs.pop('displayName', None)
    # def __init__(self, **kwargs):
    #     super(User, self).__init__(**kwargs)
    #     # do custom initialization here
    def __init__(self, resort_tuple):
        self.name = resort_tuple.name
        self.display_name = resort_tuple.displayName

    def __repr__(self):
        return '<Resort (%r %r %r)>' % (self.id, self.name, self.display_name)


# fields = ("typeName", "resortName", "displayName", "type", "maxCapacity", "bedSetup",
#           "numBedroom", "numBathroom", "kitchen", "kitchenette", "privateBath",
#           "ac", "patio", "seaview", "profilePhoto", "photos")
class Unitgroup(Base):
    __tablename__ = 'unitgroup'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    display_name = db.Column(db.String(30), nullable=False)
    active = db.Column(db.Boolean, default=True)
    resort_id = db.Column(db.Integer, db.ForeignKey('resort.id'))
    # relationship
    units = db.relationship("Unit", backref='unitgroup', lazy='dynamic')

    # input is named tuple UnitRecord
    def __init__(self, row):
        resort = Resort.query.filter(Resort.name == row.resortName).one()
        self.name = row.typeName
        self.display_name = row.displayName
        self.resort_id = resort.id

    def __repr__(self):
        return '<Unitgroup (%r %r %r)>' % (self.id, self.name, self.display_name)


class Unit(Base):
    __tablename__ = 'unit'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    display_name = db.Column(db.String(30))
    active = db.Column(db.Boolean, default=True)
    unitgroup_name = db.Column(db.String(30))
    unitgroup_id = db.Column(db.Integer, db.ForeignKey('unitgroup.id'))
    # relationships
    availabilities = db.relationship('Availability', backref='unit', lazy='dynamic')
    bookings = db.relationship('Booking', backref='unit', lazy='dynamic')

    # input is named tuple UnitNameRecord
    def __init__(self, row):
        unitgroup = Unitgroup.query.filter(Unitgroup.name == row.groupName).one()
        self.name = row.name
        self.display_name = row.displayName
        # this column is redundant but convenient
        self.unitgroup_name = row.groupName
        self.unitgroup_id = unitgroup.id

    def __repr__(self):
        return '<Unit (%r %r %r %r)>' % (self.id, self.name, self.display_name, self.unitgroup_name)


class Availability(Base):
    __tablename__ = 'availability'

    id = db.Column(db.Integer, primary_key=True)
    date_slot = db.Column(db.Date, nullable=False)
    status = db.Column(db.Integer, default=1)       # booked=1, blocked=2  ( OLD # available=1, unavailable=0, blocked=-1 )
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))

    UniqueConstraint('date_slot', 'unit_id', name='uq_date_unit')

    def __init__(self, unit_id, date_slot):
        self.unit_id = unit_id
        self.date_slot = date_slot
        self.status = 1

    def __init__(self, unit_id, date_slot, status):
        self.unit_id = unit_id
        self.date_slot = date_slot
        self.status = status

    def __repr__(self):
        return '<Availability (id = %r unit_id = %r date = %r status = %r)>' % (self.id, self.unit_id, self.date_slot, self.status)

    # FIXME - underlying design on Availability was changed on July 25
    # def is_available(self):
    #     return True if self.status == 1 else False


class Calendar(db.Model):
    __tablename__ = 'calendar'

    date_ = db.Column(db.Date, primary_key=True)

    def __repr__(self):
        return '<Calendar (id = %r)>' % self.date_


# TODO - add note field, transaction_id
# unit_name is captured as a snapshot(convenience field). source of truth is unit_id.
# Validation rule upon save : each date should be available
class Booking(Base):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    unit_name = db.Column(db.String(30))
    begin_on = db.Column(db.Date, nullable=False)
    end_on = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer)
    booked_rate = db.Column(db.Integer)
    status = db.Column(db.String(30), default='CREATED')
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(60))
    is_admin = db.Column(db.Boolean, default=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    availabilities = db.relationship('Availability', backref='booking', lazy='dynamic')
    notes = db.Column(db.String(256))
    # booking_request_id = db.Column(db.Integer, db.ForeignKey('booking_request.id'))
    #transaction_id = db.Column(db.String(30), unique=True)

    def __init__(self, unit_id, unit_name, unit_info):
        self.unit_id = unit_id
        self.unit_name = unit_name
        self.begin_on = unit_info.begin_date
        self.end_on = unit_info.end_date
        self.guests = unit_info.guests
        self.booked_rate = unit_info.avg_price

    def __repr__(self):
        return '<Booking (id = %r, unit_id = %r, begin_on = %r, end_on = %r)>' % (self.id, self.unit_id, self.begin_on, self.end_on)


class BookingRequest(Base):
    __tablename__ = 'booking_request'

    id = db.Column(db.Integer, primary_key=True)
    unitgroup_name = db.Column(db.String(30), nullable=False)
    checkin = db.Column(db.Date, nullable=False)
    checkout = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    avg_price = db.Column(db.Integer)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(60), nullable=False)
    status = db.Column(db.String(30), default='CREATED')
    stripe_id = db.Column(db.Unicode(255, collation='utf8_bin'))
    unitgroup_id = db.Column(db.Integer, db.ForeignKey('unitgroup.id'))

    def __init__(self, unitgroup_name, unitgroup_id, checkin, checkout, guests, email, unit_info):
        self.unitgroup_id = unitgroup_id
        self.unitgroup_name = unitgroup_name
        self.checkin = utils.convert_date_to_string(checkin)
        self.checkout = utils.convert_date_to_string(checkout)
        self.guests = guests
        self.unit_info = unit_info
        self.avg_price = self.unit_info.avg_price if self.unit_info.avg_price else 0
        self.firstname = None
        self.lastname = None
        self.email = email

    def __repr__(self):
        return "(unitgroup name = %s : checkin = %s checkout = %s guests = %s)" \
               % (self.unitgroup_name, self.checkin, self.checkout,  self.guests)


    def serialize_booking_request(self):
        unit_info = self.unit_info
        if unit_info is None:
            return {}
        return {
            'unitgroup_name': self.unitgroup_name,
            'display_name': unit_info.unit.displayName,
            'resort_name': unit_info.resort.displayName,
            'checkin': self.checkin,
            'checkout': self.checkout,
            'guests': self.guests,
            'email': self.email,
            'avg_price': self.avg_price
        }


# wrapper objects for query results
class BookingRequestInfo():
    def __init__(self, booking_request, unitgroup):
        self.booking_request = booking_request
        self.unitgroup = unitgroup


# wrapper objects for query results
class BookingInfo():
    def __init__(self, booking, unit):
        self.booking = booking
        self.unit = unit


class EmailData(object):
    def __init__(self, booking_request, subject, status, comment):
        self.booking_request = booking_request
        self.subject = subject
        self.status = status
        self.comment = comment


def list_booking_request_all(status, limit=100):
    # cursor = int(cursor) if cursor else 0
    query = (BookingRequest.query
             .filter(BookingRequest.status == status)
             .add_entity(Unitgroup)
             .order_by(BookingRequest.updated_on.desc())
             .limit(limit))
             # .offset(cursor))
    # requests = builtin_list(map(from_sql, query.all()))
    return query.all()


def list_booking_request(status, resort_id, limit=100):
    query = (BookingRequest.query
             .join(Unitgroup, Unitgroup.id == BookingRequest.unitgroup_id)
             .filter(Unitgroup.resort_id == resort_id)
             .filter(BookingRequest.status == status)
             .add_entity(Unitgroup)
             .order_by(BookingRequest.updated_on.desc())
             .limit(limit))
    # bookings = builtin_list(map(from_sql, query.all()))
    return query.all()


# def list_bookings_all(limit=100, cursor=None):
def list_bookings_all(limit=100):
    # cursor = int(cursor) if cursor else 0
    query = (Booking.query
             .join(Unit, Unit.id == Booking.unit_id)
             .add_entity(Unit)
             .order_by(Booking.updated_on.desc())
             .limit(limit))
             # .offset(cursor))
    # bookings = builtin_list(map(from_sql, query.all()))
    # next_page = cursor + limit if len(bookings) == limit else None
    # return (bookings, next_page)
    bookings = query.all()
    return bookings


# returns Booking and Unit info
def list_bookings(resort_id, limit=100):
    query = (Booking.query
             .join(Unit, Unit.id == Booking.unit_id)
             .join(Unitgroup, Unitgroup.id == Unit.unitgroup_id)
             .filter(Unitgroup.resort_id == resort_id)
             .add_entity(Unit)
             .order_by(Booking.updated_on.desc())
             .limit(limit))

    bookings = query.all()
    return bookings


# # get bookings that begins in this period (checking in this period)
# def get_bookings_begin(begin_date, end_date):
#     query = (Booking.query
#              .filter(Booking.begin_on.between(begin_date, end_date))
#              .order_by(Booking.begin_on, Booking.unit_id)
#     )
#     return query.all()
#
#
# # get bookings that exist in this period
# def get_bookings_all(begin_date, end_date):
#     query = (Booking.query
#              .filter(or_(Booking.begin_on.between(begin_date, end_date), func.ADDDATE(Booking.end_on, -1).between(begin_date, end_date)))
#              .order_by(Booking.begin_on, Booking.unit_id)
#     )
#     return query.all()


# get bookings that exist in this period
def get_bookings(resort_id, begin_date, end_date):
    query = (Booking.query
             .join(Unit, Unit.id == Booking.unit_id)
             .join(Unitgroup, Unitgroup.id == Unit.unitgroup_id)
             .filter(Unitgroup.resort_id == resort_id)
             .filter(or_(Booking.begin_on.between(begin_date, end_date), func.ADDDATE(Booking.end_on, -1).between(begin_date, end_date)))
             .add_entity(Unit)
             .order_by(Booking.begin_on, Booking.unit_id)
    )
    return query.all()


def read(id):
    result = Booking.query.get(id)
    if not result:
        return None
    return from_sql(result)


# join Booking with Unit for Unit meta data
def get_booking(id):
    query = (Booking.query
             .join(Unit, Unit.id == Booking.unit_id)
             .filter(Booking.id == id)
             .add_entity(Unit)
    )
    return query.first()


def create_booking(booking):
    try:
        db.session.add(booking)
        db.session.flush()
        # create availability for each date slot
        # booked = 1, blocked = 2
        for single_date in utils.daterange(booking.begin_on, booking.end_on):
            # change datetime to date
            single_date = single_date.date()
            availability = Availability(booking.unit_id, single_date, 1)
            availability.booking_id = booking.id
            db.session.add(availability)
            logging.info('[Create Availability] saving availability: with booking id %r' % booking.id)
        logging.info("[Create] Booking Success: booking id = %s", booking.id)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        msg = "ERROR on [ Create ] Booking: email = " + booking.email + ", error = " + unicode(e)
        logging.error(msg)
        raise Exception(msg)

    return from_sql(booking)


def update(data, id):
    booking = Booking.query.get(id)
    for k, v in data.items():
        setattr(booking, k, v)
    db.session.add(booking)
    db.session.flush()
    db.session.commit()

    # checkin = utils.convert_string_to_date(booking.begin_on)
    # checkout = utils.convert_string_to_date(booking.end_on)
    # unit = Unit.query.filter(Unit.id == booking.id).one()
    #
    # try:
    #     # delete all
    #     availabilities = get_availabilities_by_booking_id(id)
    #     for availability in availabilities:
    #         logging.info(availability)
    #         logging.info('[Delete Availability] deleting availability: date_slot = %s' % availability.date_slot)
    #         db.session.delete(availability)
    #
    #     # validate availability
    #     if not is_unit_available(unit.id, checkin, checkout):
    #         msg = "ERROR on [ Update ] Booking: id = " + id + "Please check the availability and try again. The Unit is NOT available for the dates you specified."
    #         logging.error(msg)
    #         raise Exception(msg)
    #
    #     # create all
    #     checkin = utils.convert_string_to_date(booking.begin_on)
    #     checkout = utils.convert_string_to_date(booking.end_on)
    #     # for single_date in utils.daterange(booking.begin_on, booking.end_on):
    #     for single_date in utils.daterange(checkin, checkout):
    #         # change datetime to date
    #         print single_date
    #         single_date = single_date.date()
    #         availability = Availability(booking.unit_id, single_date, 1)
    #         availability.booking_id = booking.id
    #         logging.info(availability)
    #         logging.info('[Create Availability] saving availability: with booking id %r' % booking.id)
    #         db.session.add(availability)
    #
    #     db.session.commit()
    # except Exception as e:
    #     db.session.rollback()
    #     msg = "ERROR on [ Update ] Booking: id = " + id + ", error = " + str(e)
    #     logging.error(msg)
    #     raise Exception(msg)

    return from_sql(booking)


def delete(id):
    try:
        # availabilities = get_availabilities(booking.unit_id, booking.begin_on, booking.end_on)
        availabilities = get_availabilities_by_booking_id(id)
        for availability in availabilities:
            logging.info(availability)
            logging.info('[Delete Availability] deleting availability: date_slot = %s' % availability.date_slot)
            db.session.delete(availability)

        logging.info('[Delete Booking] deleting booking: id = %r' % id)
        Booking.query.filter_by(id=id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        msg = "ERROR on [ Delete ] Booking: id = " + id + ", error = " + unicode(e)
        logging.error(msg)
        raise Exception(msg)


# TODO - refactor with save_entity() below
def create_entity(entity):
    db.session.add(entity)
    db.session.commit()
    return from_sql(entity)


def save_entity(entity):
    db.session.add(entity)
    db.session.commit()
    logging.info(entity)
    return entity


def delete_entity(entity):
    db.session.delete(entity)
    db.session.commit()
    logging.info(entity)
    return entity


def get_resorts():
    return Resort.query.all()


def get_resort_by_name(resort_name):
    return Resort.query.filter_by(name=resort_name).one()


def get_unitgroups(resort_id):
    return Unitgroup.query.filter_by(resort_id=resort_id).all()


def get_units():
    return Unit.query.all()


def get_units_by_group(unitgroup_id):
    query = (Unit.query
             .join(Unitgroup, Unitgroup.id == Unit.unitgroup_id)
             .filter(Unitgroup.id == unitgroup_id)
             .filter(Unit.active == 1)
             .order_by(Unit.id)
    )
    return query.all()


def get_units_by_resort(resort_id):
    #results = Unitgroup.query.join(Resort, Unitgroup.resort_id == Resort.unitgroup_id)
    # results = Unit.query.join(Unitgroup, Unitgroup.id == Unit.unitgroup_id).group_by(Unit.display_name)
    query = (Unit.query
                .join(Unitgroup, Unitgroup.id == Unit.unitgroup_id)
                .filter(Unitgroup.resort_id == resort_id)
                .filter(Unit.active == 1)
                .order_by(Unit.id)
            )
    return query.all()


def get_units_by_resort_name(resort_name):
    resort = get_resort_by_name(resort_name)
    return get_units_by_resort(resort.id)


def get_calendar_date(date):
    return Calendar.query.get(date)


def get_calendar_dates(begin, end):
    return Calendar.query.filter(Calendar.date_.between(begin, end)).all()


# FIXME - does not work on 'blocked(2)'
def is_unit_available(unit_id, checkin, checkout):
    results = get_availabilities(unit_id, checkin, checkout)
    results_by_unit = zip(*results)
    # extract status field from result set
    status_list = results_by_unit[2]
    logging.info(status_list)
    if sum(status_list) > 0:
        return False
    return True


def get_availabilities_by_booking_id(booking_id):
    query = (Availability.query
                .filter(Availability.booking_id == booking_id)
            )
    return query.all()


# 0 = avail, 1 = booked, 2= blocked
def get_availabilities(unit_id, begin_date, end_date):
    # query = (Availability.query
    #             .filter(Availability.unit_id == unit_id)
    #             .filter(Availability.date_slot.between(begin_date, end_date)))
    # return query.all()
    cmd = '''
        select c.date_ as date_slot, u.id as unit_id, IFNULL( a.status ,0) as status, a.id as id, a.booking_id as booking_id
            from calendar c
            join unit u
            left join availability a on  a.date_slot = c.date_ and a.unit_id = u.id
            where c.date_ >= :begin and c.date_ < :end and u.id = :unit_id
            order by date_slot
        '''
    availabilities = db.session.execute(
        text(cmd),
        {'unit_id': unit_id,
         'begin': begin_date,
         'end': end_date})
    return availabilities


# 0 = avail, 1 = booked, 2= blocked
def get_availability(unit_id, date_slot):
    query = (Availability.query
              .filter(Availability.unit_id == unit_id)
              .filter(Availability.date_slot == date_slot))
    list = query.all()
    if list:
        return list[0]
    return None
    # return query.limit(1).all()
#     cmd = '''
#         select IFNULL((
#             select distinct status from  availability a
#                 where a.date_slot = :date and unit_id = :unit_id), 0);
#         '''
#     availabilities = db.session.execute(
#         text(cmd),
#         {'unit_id': unit_id,
#          'date': date_slot})
#     return availabilities


# returns resorts ( id, name, count )
def search(begin_date, end_date):
    # return Resort.query.all()
    cmd = '''
            select  r.id, r.name, count(1) as count
            from resort r
            join unitgroup ug on ug.resort_id = r.id
            join unit u on u.unitgroup_id = ug.id
            where  not exists ( select 1 from availability a
            where a.unit_id = u.id and a.date_slot >= :begin and a.date_slot < :end)
            group by r.id
            '''
    resorts = db.session.execute(
        text(cmd),
        {'begin': begin_date,
         'end': end_date})
    return resorts


# returns units (id, name, available)
def search_by_resort(resortname, begin_date, end_date):
    cmd = '''
            select ug.id, ug.name, sum(
                IF(exists
                    (select 1 from availability a
                    where a.unit_id = u.id and a.date_slot >= :begin and a.date_slot < :end),
                    0, 1)) as available
            from resort r
            join unitgroup ug on ug.resort_id = r.id
            join unit u on u.unitgroup_id = ug.id
            where r.name = :resortname
            group by ug.id;
            '''
    units = db.session.execute(
        text(cmd),
        {'resortname': resortname,
         'begin': begin_date,
         'end': end_date})
    return units


def search_by_unit_group(unitgroup_name, begin_date, end_date):
    cmd = '''
            select ug.id, ug.name, sum(
                IF(exists
                    (select 1 from availability a
                    where a.unit_id = u.id and a.date_slot >= :begin and a.date_slot < :end),
                    0, 1)) as available
            from unitgroup ug
            join unit u on u.unitgroup_id = ug.id
            where ug.name = :groupname;
            '''
    units = db.session.execute(
        text(cmd),
        {'groupname': unitgroup_name,
         'begin': begin_date,
         'end': end_date})
    return units


def ping_mysql():
    db.session.execute('select 1')

# IMPORTANT :
# RUN ONLY ONCE - which should happen in local DEV, not in PROD server. (invoked from __init___)
# read CSV data and populate db.
def init_db():
    # print 'Creating all tables...................'
    # db.create_all()
    # print 'Populating all tables from CSV........'
    # populate_csv_data()
    # print '..................................Done'
    pass


# create Resort, Unit, Unitgroup records
def populate_csv_data():
    # print 'Populating data in Resort, Unitgroup and Unit tables.............'
    for row in read_data_resorts():
        create_entity(Resort(row))
    for row in read_data_units():
        create_entity(Unitgroup(row))
    for row in read_data_unitnames():
        create_entity(Unit(row))
    pass


# def _create_database():
#     app = Flask(__name__)
#     app.config.from_pyfile('../../config.py')
#     init_app(app)
#     with app.app_context():
#         db.create_all()
#     print("All tables created")
#
#
# if __name__ == '__main__':
#     _create_database()



# ----- DEPRECATED -----
# create availability records for all units for default date range
# def populate_availability_all():
#     print 'Populating Availability table.............'
#     for unit in get_units():
#         print unit.id
#         populate_availability(unit.id)
#     print 'Done'

# create availability records for given unit for default date range
# def populate_availability(unit_id):
#     for calendar in get_calendar_dates(CALENDAR_BEGIN_DATE, CALENDAR_END_DATE):
#         create_entity(Availability(unit_id, calendar.date_))

# run stored procedure - this should be faster. but the code does not work yet.
# params = {'unit_id': unit_id,
#             'start': CALENDAR_BEGIN_DATE,
#             'end': CALENDAR_END_DATE}
# results = db.session.execute('fill_availability ?, ?, ?', params)
# results = db.session.execute('fill_availability @unit_id=:unit_id, @start_date=:start, @end_date=:end', params)
# print results