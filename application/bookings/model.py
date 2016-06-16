from datetime import datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

builtin_list = list

db = SQLAlchemy()

# def get_db():
#     return db

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


class Booking(Base):
    __tablename__ = 'booking'

    id = db.Column(db.Integer, primary_key=True)
    #unit_id = db.Column(db.Integer, db.ForeignKey('units.unit_id'))
    unit_name = db.Column(db.String(30))
    begin_on = db.Column(db.DateTime, nullable=False)
    end_on = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default='CREATED')
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(60))
    is_admin = db.Column(db.Boolean, default=False)
    #transaction_id = db.Column(db.String(255), unique=True)

    def __repr__(self):
        # return "<Booking(begin_on='%s', end_on=%s)" % (self.begin_on, self.end_on)
        return '<Booking(begin_on = %r, end_on = %r)>' % (self.begin_on, self.end_on)


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


def _create_database():
    app = Flask(__name__)
    app.config.from_pyfile('../../config.py')
    init_app(app)
    with app.app_context():
        db.create_all()
    print("All tables created")


if __name__ == '__main__':
    _create_database()
