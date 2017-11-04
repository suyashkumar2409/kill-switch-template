from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class UpgradeForm(Form):
	upgradeToCreater = SubmitField('Upgrade to Quiz Creator')
	upgradeToSuperUser = SubmitField('Upgrade to Super User') 