from flask import Blueprint

superuser = Blueprint('superuser', __name__)

from . import views