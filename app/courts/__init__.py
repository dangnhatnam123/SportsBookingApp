from flask import Blueprint
courts_bp = Blueprint('courts_bp', __name__)
from app.courts import views