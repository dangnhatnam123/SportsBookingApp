from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from app.models import VaiTro


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Bạn cần đăng nhập!", "warning")
            return redirect(url_for('auth_bp.login_view'))

        if current_user.vai_tro != VaiTro.QUAN_LY:
            flash("Bạn không có quyền truy cập vào khu vực Quản trị!", "danger")
            return redirect('/')

        # 3. Hợp lệ thì cho đi tiếp
        return f(*args, **kwargs)

    return decorated_function