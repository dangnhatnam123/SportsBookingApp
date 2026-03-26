from flask import Blueprint, render_template
from flask import render_template, request, redirect, url_for
from app import app, dao, login
from flask_login import login_user, logout_user

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


@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/register', methods=['GET', 'POST'])
def register_view():
    err_msg = ''
    if request.method == 'POST':
        data = request.form
        password = data.get('password')
        confirm = data.get('confirm')

        vai_tro_chon = data.get('vai_tro')

        if password != confirm:
            err_msg = 'Mật khẩu xác nhận không khớp!'
        else:
            try:
                dao.add_user(name=data.get('name'),
                             username=data.get('username'),
                             password=password,
                             vai_tro=vai_tro_chon)
                return redirect('/login')
            except Exception as ex:
                err_msg = str(ex)

    return render_template('register.html', err_msg=err_msg)

@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

if __name__ == '__main__':
    app.run(debug=True)
