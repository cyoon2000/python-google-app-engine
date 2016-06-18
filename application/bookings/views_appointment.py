import forms
from datetime import datetime, date

from flask import (Blueprint, render_template, request, abort, flash, url_for,
                   redirect, session, current_app, jsonify)

from sqlalchemy.sql import select, and_, or_

from database import db
from flask_wtf import Form
from wtforms.fields.html5 import DateField

example_api = Blueprint('example', __name__, template_folder='templates')


@example_api.route('/example1', methods=['POST','GET'])
def example_1():
    form = forms.ExampleForm()
    if form.validate_on_submit():
        return form.dt.data.strftime('%Y-%m-%d')
    return render_template('examples/form_example.html', form=form)

@example_api.route('/example2', methods=['POST','GET'])
def example_2():
    form = forms.ExampleForm()
    if form.validate_on_submit():
        return form.dt.data.strftime('%Y-%m-%d')
    return render_template('examples/form_datepicker.html', form=form)

@example_api.route('/example3', methods=['POST','GET'])
def example_3():
    form = forms.ExampleForm()
    if form.validate_on_submit():
        return form.dt.data.strftime('%Y-%m-%d')
    return render_template('examples/schedule.html', form=form)

