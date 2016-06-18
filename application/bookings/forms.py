import datetime

from flask.ext.wtf import Form
from wtforms import (Field, HiddenField, TextField,
                     TextAreaField, SubmitField, DateField, SelectField)
from wtforms.validators import Required, Length, Email
from flask.ext.wtf.html5 import EmailField

class ExampleForm(Form):
    dt = DateField('DatePicker', format='%Y-%m-%d')