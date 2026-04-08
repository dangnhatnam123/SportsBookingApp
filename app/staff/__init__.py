from flask import Blueprint
staff_bp = Blueprint('staff_bp', __name__)
from app.staff import views