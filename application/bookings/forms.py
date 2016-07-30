import datetime
import model, views #, utils

from flask_wtf import Form
from wtforms import StringField, IntegerField, DateField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, InputRequired, Email
from application.common import utils


class ExampleForm(Form):
    dt = DateField('DatePicker', format='%Y-%m-%d')


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

        print 'Checking availability...........................'
        # TODO - FIXME - user input does not change these values once instantiate the form
        print self.begin_on.data
        print self.end_on.data
        for availability in model.get_availabilities(self.unit_id.data, self.begin_on.data, self.end_on.data):
            if availability.is_available() is False:
                self.end_on.errors.append('Not available on %r' % utils.convert_date_to_string(availability.date_slot))

        if self.end_on.errors:
            return False

        return True

