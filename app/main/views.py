from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User
from ..email import send_email
from . import main
from .forms import NameForm
from flask_login import current_user

@main.route('/')
def index():
    if current_user.is_authenticated:
        role_id = User.query.filter_by(id=current_user.get_id()).first().role_id
    else:
        role_id = -1
    return render_template('index.html', role_id = role_id, user = current_user)
