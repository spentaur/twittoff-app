from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired
from app.api.twitter import twitter_user_exists
from wtforms import ValidationError


def valid_screenname(form, field):
    if not twitter_user_exists(field.data):
        raise ValidationError('Not a valid screen name.')


class NewUserForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(), valid_screenname])
