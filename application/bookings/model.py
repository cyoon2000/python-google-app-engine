import logging
import utils
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from database import db
from application.contents.data import read_data_resorts, read_data_units, read_data_unitnames

builtin_list = list

CALENDAR_BEGIN_DATE = '2016-07-01'
CALENDAR_END_DATE = '2017-06-30'

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
    #created_by = db.Column(db.String(64), default=lambda: current_user.username)
    #updated_by = db.Column(db.String(64), default=lambda: current_user.username)


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
    unitgroup_id = db.Column(db.Integer, db.ForeignKey('unitgroup.id'))
    # relationships
    availabilities = db.relationship('Availability', backref='unit', lazy='dynamic')
    bookings = db.relationship('Booking', backref='unit', lazy='dynamic')

    # input is named tuple UnitNameRecord
    def __init__(self, row):
        unitgroup = Unitgroup.query.filter(Unitgroup.name == row.groupName).one()
        self.name = row.name
        self.display_name = row.displayName
        self.unitgroup_id = unitgroup.id

    def __repr__(self):
        return '<Unit (%r %r %r)>' % (self.id, self.name, self.display_name)


# TODO - add note field, transaction_id(UUID), payment_id (payment table does not exist yet)
# unit_name is captured as a snapshot(convenience field). source of truth is unit_id.
# Validation rule upon save : each date should be available
class Booking(Base):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    unit_name = db.Column(db.String(30))
    begin_on = db.Column(db.DateTime, nullable=False)
    end_on = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default='CREATED')
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(60))
    is_admin = db.Column(db.Boolean, default=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    availabilities = db.relationship('Availability', backref='booking', lazy='dynamic')
    #transaction_id = db.Column(db.String(255), unique=True)

    def __repr__(self):
        return '<Booking (id = %r, unit_id = %, begin_on = %r, end_on = %r)>' % (self.id, self.unit_id, self.begin_on, self.end_on)


class Availability(Base):
    __tablename__ = 'availability'

    id = db.Column(db.Integer, primary_key=True)
    date_slot = db.Column(db.Date, nullable=False)
    status = db.Column(db.Integer, default=1)    #available=1, unavailable=0, blocked=-1
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))

    def __init__(self, unit_id, date_slot):
        self.unit_id = unit_id
        self.date_slot = date_slot
        self.status = 1

    def __repr__(self):
        return '<Availability (id = %r unit_id = %r date = %r status = %r)>' % (self.id, self.unit_id, self.date_slot, self.status)


class Calendar(db.Model):
    __tablename__ = 'calendar'

    date_ = db.Column(db.Date, primary_key=True)

    def __repr__(self):
        return '<Calendar (id = %r)>' % self.date_


def list(limit=10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (Booking.query
             .order_by(Booking.unit_name)
             .limit(limit)
             .offset(cursor))
    bookings = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(bookings) == limit else None
    return (bookings, next_page)


def read(id):
    result = Booking.query.get(id)
    if not result:
        return None
    return from_sql(result)


def create(data):
    entry = Booking(**data)
    db.session.add(entry)
    db.session.commit()
    return from_sql(entry)


def update(data, id):
    entry = Booking.query.get(id)
    for k, v in data.items():
        setattr(entry, k, v)
    db.session.commit()
    return from_sql(entry)


def delete(id):
    Booking.query.filter_by(id=id).delete()
    db.session.commit()

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


def get_resorts():
    return Resort.query.all()


def get_unitgroups(resort_id):
    return Unitgroup.query.filter_by(resort_id=resort_id).all()


def get_units():
    return Unit.query.all()


def get_units_by_resort(resort_id):
    #results = Unitgroup.query.join(Resort, Unitgroup.resort_id == Resort.unitgroup_id)
    # results = Unit.query.join(Unitgroup, Unitgroup.id == Unit.unitgroup_id).group_by(Unit.display_name)
    query = (Unit.query
                .join(Unitgroup, Unitgroup.id == Unit.unitgroup_id)
                .filter(Unitgroup.resort_id == resort_id)
                .filter(Unit.active == 1)
            )
    return query.all()


def get_calendar_date(date):
    return Calendar.query.get(date)


def get_calendar_dates(begin, end):
    return Calendar.query.filter(Calendar.date_.between(begin, end)).all()


def get_availabilities(unit_id, begin_date, end_date):
    query = (Availability.query
                .filter(Availability.unit_id == unit_id)
                .filter(Availability.date_slot.between(begin_date, end_date)))
    return query.all()


def get_availability(unit_id, date):
    query = (Availability.query
             .filter(Availability.unit_id == unit_id)
             .filter(Availability.date_slot == date))
    return query.one()


def is_available(unit_id, date):
    availability = get_availability(unit_id, date)
    return True if (availability.status == 1) else False



# IMPORTANT :
# RUN ONLY ONCE - which should happen in local DEV, not in PROD server. (invoked from __init___)
# read CSV data and populate db.
def init_db():
    print 'Creating all tables...................'
    db.create_all()
    populate_csv_data()

    # this takes too long.  use stored procedure
    #populate_availability_all()
    print '..................................Done'


# create Resort, Unit, Unitgroup records
def populate_csv_data():
    print 'Populating data in Resort, Unitgroup and Unit tables.............'
    for row in read_data_resorts():
        create_entity(Resort(row))
    for row in read_data_units():
        create_entity(Unitgroup(row))
    for row in read_data_unitnames():
        create_entity(Unit(row))


# create availability records for all units for default date range
def populate_availability_all():
    print 'Populating Availability table.............'
    for unit in get_units():
        print unit.id
        populate_availability(unit.id)
    print 'Done'


# create availability records for given unit for default date range
def populate_availability(unit_id):
    print '(for unit_id = %r)' % unit_id
    for calendar in get_calendar_dates(CALENDAR_BEGIN_DATE, CALENDAR_END_DATE):
        create_entity(Availability(unit_id, calendar.date_))

    # run stored procedure - this should be faster. but the code does not work yet.
    # params = {'unit_id': unit_id,
    #             'start': CALENDAR_BEGIN_DATE,
    #             'end': CALENDAR_END_DATE}
    # results = db.session.execute('fill_availability ?, ?, ?', params)
    # results = db.session.execute('fill_availability @unit_id=:unit_id, @start_date=:start, @end_date=:end', params)
    # print results


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
