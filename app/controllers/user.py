from flask import Blueprint, redirect
from app.forms.NewUserForm import NewUserForm
from app.models.user import User
from app.models.user import Tweet
from flask import render_template

blueprint = Blueprint('user', __name__)


@blueprint.route('/user/add', methods=['GET', 'POST'])
def new_user():
    form = NewUserForm()

    if form.validate_on_submit():
        db_user = User.add_user(form.username.data)
        Tweet.add_user_tweets(db_user)
        return redirect('/')
    return render_template('user/add.html', form=form)
