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
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            if user.vai_tro == VaiTro.QUAN_LY:
                return redirect('/admin/manage_san')

            else :
                return redirect('/')


        else:
            err_msg = 'Tên đăng nhập hoặc mật khẩu không chính xác!'

    return render_template('login.html', err_msg=err_msg)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register_view():
    err_msg = ''
    if request.method == 'POST':
        data = request.form
        name = data.get('name', '').strip()
        username = data.get('username', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        confirm = data.get('confirm', '')

        if not name or not username or not password or not phone:
            err_msg = 'Vui lòng điền đầy đủ các thông tin!'
        elif not re.match(r'^0\d{9}$', phone):
            err_msg = 'Số điện thoại không hợp lệ (phải bắt đầu bằng 0 và có 10 chữ số)!'
        elif len(password) < 6:
            err_msg = 'Mật khẩu phải có ít nhất 6 ký tự!'
        elif password != confirm:
            err_msg = 'Mật khẩu xác nhận không khớp!'
        else:
            try:
                if dao.check_existing_user(username, phone):
                    err_msg = 'Tên đăng nhập hoặc số điện thoại đã tồn tại!'
                else:
                    otp_code = str(random.randint(100000, 999999))
                    print(f"========== OTP CỦA BẠN LÀ: {otp_code} ==========")
                    session['temp_user'] = {
                        'name': name,
                        'username': username,
                        'phone': phone,
                        'password': password
                    }
                    session['otp_code'] = otp_code
                    return redirect(url_for('auth_bp.verify_otp'))

            except Exception as ex:
                err_msg = str(ex)

        return render_template('register.html', err_msg=err_msg)


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'temp_user' not in session:
        return redirect(url_for('auth_bp.register_view'))

    err_msg = ''
    if request.method == 'POST':
        user_otp = request.form.get('otp', '').strip()

        # Kiểm tra mã OTP
        if user_otp == session.get('otp_code'):
            user_data = session['temp_user']
            try:
                # Nếu đúng mã -> Lưu chính thức vào database
                dao.add_user(name=user_data['name'],
                             username=user_data['username'],
                             password=user_data['password'],
                             phone=user_data['phone'])

                # Xóa dữ liệu tạm trong session
                session.pop('temp_user', None)
                session.pop('otp_code', None)

                flash('Đăng ký tài khoản thành công! Vui lòng đăng nhập.', 'success')
                return redirect('/login')
            except Exception as ex:
                err_msg = str(ex)
        else:
            # Nếu sai mã -> Không chuyển trang, hiện thông báo lỗi
            err_msg = 'Mã OTP không chính xác. Vui lòng kiểm tra lại!'

    return render_template('verify_otp.html', err_msg=err_msg)


@auth_bp.route('/resend-otp')
def resend_otp():
    if 'temp_user' in session:
        # Tạo mã mới
        new_otp = str(random.randint(100000, 999999))
        session['otp_code'] = new_otp

        # Mock gửi SMS bằng cách in ra console
        print(f"========== MÃ OTP MỚI CỦA BẠN LÀ: {new_otp} ==========")

        flash('Mã OTP mới đã được gửi!', 'info')
        return redirect(url_for('auth_bp.verify_otp'))

    return redirect(url_for('auth_bp.register_view'))


@auth_bp.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)
