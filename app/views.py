from flask import Blueprint, render_template

main_bp = Blueprint('main_bp', __name__, template_folder='templates')
@main_bp.route('/admin')
def admin():
    return render_template('admin/admin.html')

@main_bp.route('/')
def home():
    return render_template('main.html')

@main_bp.route('/services')
def services():
    return "Danh sách các dịch vụ thể thao hiện có..."


