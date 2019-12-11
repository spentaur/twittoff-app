from flask import Blueprint, render_template
from app.models.user import User
from app.forms.PredictTweetForm import PredictTweetForm

blueprint = Blueprint('home', __name__)


@blueprint.route('/')
def index():
    form = PredictTweetForm()
    users = User.get_newest()
    return render_template('home/index.html', users=users, form=form)
