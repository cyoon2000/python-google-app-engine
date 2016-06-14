from application import get_model

# Import the Flask Framework
from flask import current_app, Blueprint, redirect, render_template, request, url_for

sample = Blueprint('sample', __name__, template_folder='templates')

@sample.route("/")
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')

    entries, next_page_token = get_model().list(cursor=token)

    try: return render_template(
        "list.html",
        entries=entries,
        next_page_token=next_page_token)
    except TemplateNotFound:
        abort(404)

@sample.route('/<id>')
def view(id):
    entry = get_model().read(id)
    return render_template("view.html", entry=entry)


# [START add]
@sample.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        entry = get_model().create(data)

        return redirect(url_for('.view', id=entry['id']))

    return render_template("form.html", action="Add", entry={})
# [END add]


@sample.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    entry = get_model().read(id)

    if request.method == 'POST':
        data = request.form.to_dict(flat=True)

        entry = get_model().update(data, id)

        return redirect(url_for('.view', id=entry['id']))

    return render_template("form.html", action="Edit", entry=entry)


@sample.route('/<id>/delete')
def delete(id):
    get_model().delete(id)
    return redirect(url_for('.list'))