from flask import Blueprint
booking_bp = Blueprint('booking_bp', __name__)
from app.booking import views