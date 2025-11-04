from flask import Blueprint

bp = Blueprint('appointments', __name__)

from app.api.appointments import routes