from flask import Blueprint

bp = Blueprint('medical', __name__)

from app.api.medical import routes