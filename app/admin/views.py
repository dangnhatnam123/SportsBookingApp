from werkzeug.utils import redirect
from app.admin import admin_bp


@admin_bp.route('/admin')
def index():
    return redirect('/admin')