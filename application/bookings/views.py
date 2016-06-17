from . import get_model

# Import the Flask Framework
from flask import current_app, Blueprint, redirect, render_template, request, url_for

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

