from flask import Blueprint

properties_bp = Blueprint(
    "properties",
    __name__,
    url_prefix="/properties",
)

from app.properties import routes