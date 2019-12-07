from flask import Blueprint, request, redirect, url_for

from app.models.user import User

blueprint = Blueprint('user', __name__)


@blueprint.route('/user/new', methods=['POST'])
def new_user():
    if 'username' not in request.form:
        return '', 500

    User.add_user(request.form.get('username'))

    return redirect(url_for('home.index'))
