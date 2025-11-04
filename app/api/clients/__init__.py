from flask import Blueprint

bp = Blueprint('clients', __name__)

from app.api.clients import routes