import random
import re

from app.extention import login_manager
from flask import request, redirect, render_template, url_for, session, flash
from flask_login import login_user, logout_user
from app.auth import dao
from app.auth import auth_bp
from app.models import VaiTro


@auth_bp.route('/login', methods=['GET', 'POST'])
def login_view():
    err_msg = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            err_msg = 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!'
        else:
            user = dao.auth_user(username=username, password=password)
            if user:
                login_user(user=user)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                if user.vai_tro == VaiTro.QUAN_LY:
                    return redirect('/admin/manage_san')
                return redirect('/')
            else:
                err_msg = 'Tên đăng nhập, mật khẩu không chính xác hoặc tài khoản đã bị khóa!'

    return render_template('login.html', err_msg=err_msg)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register_view():
    err_msg = ''
    if request.method == 'POST':
        data = request.form
        name = data.get('name', '').strip()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        confirm = data.get('confirm', '')
        avatar = request.files.get('avatar')

        if not all([name, username, email, phone, password]):
            err_msg = 'Vui lòng điền đầy đủ tất cả các thông tin!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            err_msg = 'Địa chỉ Email không hợp lệ!'
        elif not re.match(r'^0\d{9}$', phone):
            err_msg = 'Số điện thoại phải có 10 chữ số và bắt đầu bằng số 0!'
        elif password != confirm:
            err_msg = 'Mật khẩu xác nhận không khớp!'
        else:
            try:
                dao.add_user(name=name, username=username, password=password,
                             phone=phone, email=email, avatar=avatar)

                flash('Đăng ký thành công! Chào mừng bạn gia nhập HiSport.', 'success')
                return redirect(url_for('auth_bp.login_view'))
            except Exception as ex:
                err_msg = str(ex)

    return render_template('register.html', err_msg=err_msg)

@auth_bp.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)
