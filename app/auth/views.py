from app.extention import login_manager
from flask import request, redirect, render_template, url_for
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


@auth_bp.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@login_manager.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)
