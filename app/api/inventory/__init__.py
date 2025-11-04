from flask import Blueprint

bp = Blueprint('inventory', __name__)

from app.api.inventory import routes