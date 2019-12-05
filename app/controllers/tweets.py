from flask import Blueprint, request, redirect, url_for

from app.models.user import User
from app.models.tweet import Tweet

blueprint = Blueprint('tweets', __name__)


@blueprint.route('/tweet/new', methods=['POST'])
def new_tweet():
    if 'username' not in request.form or 'tweet' not in request.form:
        return '', 500

    user = User.query.filter_by(username=request.form.get('username')).first()

    if not user:
        return '', 500

    Tweet.add_tweet(user, request.form.get('tweet'))

    return redirect(url_for('home.index'))
