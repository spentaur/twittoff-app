from flask import Blueprint, render_template
from app.models.user import User
from app.models.tweet import Tweet

blueprint = Blueprint('home', __name__)


@blueprint.route('/')
def index():
    users = User.get_ten_newest()
    tweets = Tweet.get_ten_newest()
    return render_template('home/index.html', users=users, tweets=tweets)
