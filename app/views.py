import math
from datetime import datetime, date

from flask import Blueprint, render_template, current_app, session, jsonify
from flask import render_template, request, redirect, url_for
from app import app, dao, login, models, urls
from flask_login import login_user, logout_user, login_required, current_user

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


@main_bp.route('/search', methods= ['GET', 'POST'])
@login_required
def book_san():
    san_id = request.args.get('san_id')
    ngay_str = request.args.get('ngay')
    gio_bd_str = request.args.get('gio_bd')
    gio_kt_str = request.args.get('gio_kt')
    page = request.args.get('page', 1, type=int)

    ngay_dat = datetime.strptime(ngay_str, '%Y-%m-%d').date()
    t1 = datetime.strptime(gio_bd_str, '%H:%M').time()
    t2 = datetime.strptime(gio_kt_str, '%H:%M').time()




@main_bp.route('/checkout/<int:san_id>')
@login_required
def checkout_view(san_id):
    ngay = request.args.get('ngay')
    gio_bd = request.args.get('gio_bd')
    gio_kt = request.args.get('gio_kt')

    if not ngay or not gio_bd or not gio_kt:
        return redirect(url_for('main_bp.booking_view'))

    san = dao.get_san_by_id(san_id)
    if not san:
        return redirect(url_for('main_bp.booking_view'))

    fmt = '%H:%M'
    t1 = datetime.strptime(gio_bd, fmt)
    t2 = datetime.strptime(gio_kt, fmt)
    tong_gio = (t2 - t1).total_seconds() / 3600
    tong_tien = tong_gio * san.gia_san_theo_gio

    return render_template('checkout.html',
                           san=san, ngay=ngay, gio_bd=gio_bd,
                           gio_kt=gio_kt, tong_gio=tong_gio, tong_tien=tong_tien)


@main_bp.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    san_id = request.form.get('san_id')
    ngay = request.form.get('ngay')
    gio_bd = request.form.get('gio_bd')
    gio_kt = request.form.get('gio_kt')
    tong_tien = request.form.get('tong_tien')

    thanh_cong = dao.luu_dat_san(
        ma_nd=current_user.id,
        ma_san=san_id,
        ngay_choi=ngay,
        gio_bd=gio_bd,
        gio_kt=gio_kt,
        tong_tien=tong_tien
    )

    if thanh_cong:
         return "<h2 style='color:green; text-align:center;'>Thanh toán thành công! Sân đã được đặt.</h2><div style='text-align:center;'><a href='/'>Trở về trang chủ</a></div>"
    else:
        return "<h2 style='color:red; text-align:center;'>Có lỗi xảy ra, vui lòng thử lại!</h2>"
