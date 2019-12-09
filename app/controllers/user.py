from flask import Blueprint, redirect
from app.forms.NewUserForm import NewUserForm
from app.models.user import User
from app.models.user import Tweet
from flask import render_template
from sqlalchemy import func
from flask import abort

blueprint = Blueprint('user', __name__)


@blueprint.route('/user/add', methods=['GET', 'POST'])
def new_user():
    form = NewUserForm()

    if form.validate_on_submit():
        db_user = User.add_user(form.username.data)
        Tweet.add_user_tweets(db_user)
        return redirect(f'/user/{db_user.username}')
    return render_template('user/add.html', form=form)


@blueprint.route('/user/<username>')
def get_user(username):
    user = User.query.filter(
        func.lower(User.username) == func.lower(username)).first()
    if not user:
        abort(404)

    tweets = user.get_newest_tweets()

    return render_template('user/user.html', user=user, tweets=tweets)


@blueprint.route('/user/<username>/delete', methods=['GET', 'POST'])
def delete_user(username):
    user = User.query.filter(
        func.lower(User.username) == func.lower(username)).first()
    if not user:
        abort(404)

    return render_template('user/user.html', user=user)
