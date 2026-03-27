import math
from datetime import datetime

from flask import Blueprint, render_template, current_app
from flask import render_template, request, redirect, url_for
from app import app, dao, login, models
from flask_login import login_user, logout_user

main_bp = Blueprint('main_bp', __name__, template_folder='templates')


@main_bp.route('/admin')
def admin():
    return render_template('admin/admin.html')


@main_bp.route('/')
def home():
    return render_template('main.html',LoaiSan=models.LoaiSan)


@main_bp.route('/services')
def services():
    return "Danh sách các dịch vụ thể thao hiện có..."


@main_bp.route('/login', methods=['GET', 'POST'])
def login_view():
    err_msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else '/')
        else:
            err_msg = 'Tên đăng nhập hoặc mật khẩu không chính xác!'

    return render_template('login.html', err_msg=err_msg)


@main_bp.route('/register', methods=['GET', 'POST'])
def register_view():
    err_msg = ''
    if request.method == 'POST':
        data = request.form
        password = data.get('password')
        confirm = data.get('confirm')

        if password != confirm:
            err_msg = 'Mật khẩu xác nhận không khớp!'
        else:
            try:
                avatar_file = request.files.get('avatar')

                dao.add_user(name=data.get('name'),
                             username=data.get('username'),
                             password=password,
                             avatar=avatar_file)
                return redirect('/login')
            except Exception as ex:
                err_msg = str(ex)

    return render_template('register.html', err_msg=err_msg)


@main_bp.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@main_bp.route('/search')
def booking_view():
    kw = request.args.get('kw')
    loai = request.args.get('loai_san')
    ngay_str = request.args.get('ngay')
    gio_bd_str = request.args.get('gio_bd')
    gio_kt_str = request.args.get('gio_kt')
    page = request.args.get('page', 1, type=int)

    ngay = datetime.strptime(ngay_str, '%Y-%m-%d').date() if ngay_str else None
    t1 = datetime.strptime(gio_bd_str, '%H:%M').time() if gio_bd_str else None
    t2 = datetime.strptime(gio_kt_str, '%H:%M').time() if gio_kt_str else None

    danh_sach = dao.load_san_trong(kw=kw, loai_san_val=loai, ngay=ngay, gio_bd=t1, gio_kt=t2, page=page)
    total = dao.count_san_trong(kw=kw, loai_san_val=loai, ngay=ngay, gio_bd=t1, gio_kt=t2)
    pages = math.ceil(total / current_app.config['PAGE_SIZE'])

    return render_template('search.html',
                           danh_sach_san=danh_sach,
                           pages=pages,
                           current_page=page,
                           kw=kw, loai_san=loai, ngay=ngay_str, gio_bd=gio_bd_str, gio_kt=gio_kt_str,
                           LoaiSan=models.LoaiSan,
                           stats=dao.count_san_by_type())


if __name__ == '__main__':
    app.run(debug=True)
