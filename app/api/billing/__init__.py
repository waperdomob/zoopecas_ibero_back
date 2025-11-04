from flask import Blueprint

bp = Blueprint('billing', __name__)

from app.api.billing import routes