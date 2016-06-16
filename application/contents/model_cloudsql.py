from data import read_data_resorts, read_data_units, read_data_unitnames
from datetime import datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

builtin_list = list

db = SQLAlchemy()


# def get_db():
#     return db

# run only once
def populate_csv_data():
    print 'populate_csv_data() is disabled'
    # for row in read_data_resorts():
    #     create(Resort(row))
    # for row in read_data_units():
    #     create(UnitGroup(row))
    # for row in read_data_unitnames():
    #     print row
    #     create(Unit(row))

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


class Resort(Base):
    __tablename__ = 'resort'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    display_name = db.Column(db.String(30), nullable=False)
    active = db.Column(db.Boolean, default=True)

    unit_groups = db.relationship("UnitGroup", backref='resort')

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
        return '<Resort (%r %r)>' % (self.name, self.display_name)

# fields = ("typeName", "resortName", "displayName", "type", "maxCapacity", "bedSetup",
#           "numBedroom", "numBathroom", "kitchen", "kitchenette", "privateBath",
#           "ac", "patio", "seaview", "profilePhoto", "photos")
class UnitGroup(Base):
    __tablename__ = 'unit_group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    display_name = db.Column(db.String(30), nullable=False)
    active = db.Column(db.Boolean, default=True)

    resort_id = db.Column(db.Integer, db.ForeignKey('resort.id'))
    units = db.relationship("Unit", backref='unit_group', lazy='dynamic')

    # input is named tuple UnitRecord
    def __init__(self, row):
        resort = Resort.query.filter(Resort.name == row.resortName).one()
        self.name = row.typeName
        self.display_name = row.displayName
        self.resort_id = resort.id


    def __repr__(self):
        return '<UnitGroup (%r %r)>' % (self.name, self.display_name)


class Unit(Base):
    __tablename__ = 'unit'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    display_name = db.Column(db.String(30))
    active = db.Column(db.Boolean, default=True)

    unit_group_id = db.Column(db.Integer, db.ForeignKey('unit_group.id'))

    # input is named tuple UnitNameRecord
    def __init__(self, row):
        print row
        unit_group = UnitGroup.query.filter(UnitGroup.name == row.groupName).one()
        self.name = row.name
        self.display_name = row.displayName
        self.unit_group_id = unit_group.id

    def __repr__(self):
        return '<Unit (%r %r)>' % (self.name, self.display_name)


def create(entity):
    db.session.add(entity)
    db.session.commit()
    return from_sql(entity)


def _create_database():
    app = Flask(__name__)
    app.config.from_pyfile('../../config.py')
    init_app(app)
    with app.app_context():
        db.create_all()
    print("All tables created")


if __name__ == '__main__':
    _create_database()