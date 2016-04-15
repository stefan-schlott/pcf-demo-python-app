from flask_wtf import Form
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, URL

class SenderForm(Form):
    url=StringField('Destination URL to call (Copy it from the right place) : ' , validators=[DataRequired()])
    amountOfCalls = IntegerField('How many calls should be made (between 1 and 1000): ', validators=[DataRequired(), NumberRange(min=1,max=1000)])
    submit = SubmitField('Go for it!')
