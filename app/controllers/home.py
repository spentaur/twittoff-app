from flask import Blueprint, render_template
from app.models.user import User

blueprint = Blueprint('home', __name__)


@blueprint.route('/')
def index():
    users = User.get_newest()
    return render_template('home/index.html', users=users)
