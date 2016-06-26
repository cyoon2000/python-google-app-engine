import datetime
import model, views

from flask_wtf import Form
from wtforms import StringField, IntegerField, DateField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, InputRequired, Email


class ExampleForm(Form):
    dt = DateField('DatePicker', format='%Y-%m-%d')


class SelectForm(Form):
    unitnames = ['Casa 1', 'Casa 2']
    unit_name = SelectField(u'Unit Name', validators=[DataRequired()], choices=[(r, r) for r in unitnames])


class BookingForm(Form):
    unit_id = SelectField('Unit', coerce=int, validators=[InputRequired()])
    begin_on = DateField('Begin Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_on = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired(), Email()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        return True

