import math
from datetime import datetime, date, timedelta
from flask import Blueprint, current_app, flash
from flask import render_template, request, redirect, url_for
from app import app, dao, login, models, db
from flask_login import login_user, logout_user, login_required, current_user

from app.models import DatLich

main_bp = Blueprint('main_bp', __name__, template_folder='templates')


@main_bp.route('/admin')
def admin():
    return render_template('admin/admin.html')


@main_bp.route('/')
def home():
    return render_template('main.html', LoaiSan=models.LoaiSan)


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
    ngay_chon = request.args.get('ngay')
    gio_bd = request.args.get('gio_bd')
    gio_kt = request.args.get('gio_kt')
    page = request.args.get('page', 1, type=int)

    today = date.today()
    err_msg = ""
    DS = []
    pages = 0
    total = 0
    ngay = None
    t1 = None
    t2 = None

    if ngay_chon and gio_bd and gio_kt:
        try:
            ngay = datetime.strptime(ngay_chon, '%Y-%m-%d').date()
            t1 = datetime.strptime(gio_bd, '%H:%M').time()
            t2 = datetime.strptime(gio_kt, '%H:%M').time()

            tong_phut_bd = t1.hour * 60 + t1.minute
            tong_phut_kt = t2.hour * 60 + t2.minute
            so_phut_choi = tong_phut_kt - tong_phut_bd

            if ngay < today:
                err_msg = "Lỗi: Không thể tìm sân trong quá khứ!"
            elif ngay == today and t1 < datetime.now().time():
                err_msg = "Lỗi: Vui lòng chọn giờ khác, không được chọn giờ tỏng quá khứ!"
            elif so_phut_choi <= 0:
                err_msg = "Lỗi: Giờ kết thúc phải lớn hơn giờ bắt đầu!"
            elif so_phut_choi < 60:
                err_msg = "Lỗi: Thời gian thuê tối thiểu phải là 1 tiếng!"

        except ValueError:
            err_msg = "Lỗi: Định dạng ngày giờ không hợp lệ!"

    if not err_msg:
        DS = dao.load_san_trong(kw=kw, loai_san_val=loai, ngay=ngay, gio_bd=t1, gio_kt=t2, page=page)
        total = dao.count_san_trong(kw=kw, loai_san_val=loai, ngay=ngay, gio_bd=t1, gio_kt=t2)

        if total > 0:
            pages = math.ceil(total / current_app.config.get('PAGE_SIZE', 6))

    return render_template('search.html',danh_sach_san=DS,pages=pages,
                           current_page=page,kw=kw, loai_san=loai, ngay=ngay_chon, gio_bd=gio_bd, gio_kt=gio_kt,
                           LoaiSan=models.LoaiSan,stats=dao.count_san_by_type(),today=today,err_msg=err_msg)



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


@main_bp.route('/orders')
@login_required
def history_view():
    # Lấy trang hiện tại từ URL, mặc định là trang 1
    page = request.args.get('page', 1, type=int)

    # Gọi hàm dao lấy danh sách sân của trang đó và tổng số trang
    history_list, total_pages = dao.get_history_by_user(current_user.id, page=page)

    now = datetime.now()

    return render_template('history.html',
                           history=history_list,
                           pages=total_pages,
                           current_page=page,
                           now=now,
                           datetime=datetime)


@main_bp.route('/huy-dat-san/<int:ma_dat_san>', methods=['POST'])
@login_required
def process_huy_dat(ma_dat_san):
    dat_lich = DatLich.query.get_or_404(ma_dat_san)

    # Ràng buộc 2.1
    if dat_lich.ma_nd != current_user.id:
        flash('Lỗi: Bạn không có quyền hủy lịch đặt sân của người khác!', 'danger')
        return redirect(url_for('main_bp.history_view'))

    # Ràng buộc 2.2
    now = datetime.now()
    thoi_gian_bat_dau = datetime.combine(dat_lich.ngay_choi, dat_lich.gio_bd)
    if now >= thoi_gian_bat_dau:
        flash('Lỗi: Đã tới hoặc qua giờ nhận sân, bạn không thể hủy đơn này!', 'danger')
        return redirect(url_for('main_bp.history_view'))

    thoi_gian_con_lai = thoi_gian_bat_dau - now
    if thoi_gian_con_lai < timedelta(hours=2):
        flash('Lỗi: Bạn chỉ được phép hủy sân trước giờ chơi ít nhất 2 tiếng!', 'danger')
        return redirect(url_for('main_bp.history_view'))

    if dao.huy_dat_san(ma_dat_san):
        flash('Hủy đặt sân thành công!', 'success')
        return redirect(url_for('main_bp.history_view'))

    flash('Có lỗi xảy ra khi hủy đặt sân!', 'danger')
    return redirect(url_for('main_bp.history_view'))