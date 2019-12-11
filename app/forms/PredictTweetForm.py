from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length


class PredictTweetForm(FlaskForm):
    tweet = StringField('Tweet',
                        validators=[InputRequired(), Length(max=500)])
