from flask_wtf import Form
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, URL
import config

class SenderForm(Form):
    amountOfCalls = IntegerField('How many calls should be made (between 1 and '+str(config.maxAmountOfCalls)+'): ',
                                 validators=[DataRequired(), NumberRange(min=1,max=config.maxAmountOfCalls)])
    submit = SubmitField('Go for it!')
