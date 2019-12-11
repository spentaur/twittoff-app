from flask import Blueprint, redirect
from app.forms.NewUserForm import NewUserForm
from app.models.user import User
from app.models.tweet import Tweet
from flask import render_template
from sqlalchemy import func
from flask import abort
from flask_wtf import FlaskForm
from app.extensions import db
from .predict import train

blueprint = Blueprint('user', __name__)


@blueprint.route('/user/add', methods=['GET', 'POST'])
def new_user():
    form = NewUserForm()

    if form.validate_on_submit():
        for user in form.username.data.split(","):
            username = user.strip()
            db_user = User.add_user(username)
            Tweet.add_user_tweets(db_user)
            train()
            print(f"done with {user.strip()}")
            print("\n")
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
    form = FlaskForm()

    user = User.query.filter(
        func.lower(User.username) == func.lower(username)).first()
    if not user:
        abort(404)

    if form.validate_on_submit():
        db.session.delete(user)
        db.session.commit()

        return redirect('/')

    return render_template('user/delete.html', user=user, form=form)
