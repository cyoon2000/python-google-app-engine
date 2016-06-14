from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

builtin_list = list

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)


def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data


class Entry(db.Model):
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    guestName = db.Column(db.String(255))
    content = db.Column(db.String(255))

    def __repr__(self):
        return "<Entry(guestName='%s', content=%s)" % (self.guestName, self.content)


def list(limit=10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (Entry.query
             .order_by(Entry.guestName)
             .limit(limit)
             .offset(cursor))
    entries = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(entries) == limit else None
    return (entries, next_page)


def read(id):
    result = Entry.query.get(id)
    if not result:
        return None
    return from_sql(result)


def create(data):
    entry = Entry(**data)
    db.session.add(entry)
    db.session.commit()
    return from_sql(entry)


def update(data, id):
    entry = Entry.query.get(id)
    for k, v in data.items():
        setattr(entry, k, v)
    db.session.commit()
    return from_sql(entry)


def delete(id):
    Entry.query.filter_by(id=id).delete()
    db.session.commit()

#
# def _create_database():
#     """
#     If this script is run directly, create all the tables necessary to run the
#     application.
#     """
#     app = Flask(__name__)
#     app.config.from_pyfile('../config.py')
#     init_app(app)
#     with app.app_context():
#         db.create_all()
#     print("All tables created")

#
# if __name__ == '__main__':
#     _create_database()
