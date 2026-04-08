from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import VaiTro
from datetime import datetime
from . import staff_bp
from app.staff import dao


@staff_bp.route('/staff/dashboard')
@login_required
def staff_dashboard():
    if current_user.vai_tro != VaiTro.NHAN_VIEN:
        return redirect('/')

    ngay_str = request.args.get('ngay')
    if ngay_str:
        ngay_chon = datetime.strptime(ngay_str, '%Y-%m-%d').date()
    else:
        ngay_chon = datetime.now().date()

    ds_lich = dao.get_ds_lich_trong_ngay(ngay_chon)

    return render_template('staff/dashboard.html',
                           ds_lich=ds_lich,
                           ngay_chon=ngay_chon.strftime('%Y-%m-%d'))


@staff_bp.route('/staff/confirm-checkin/<int:booking_id>', methods=['POST'])
@login_required
def confirm_checkin(booking_id):
    lich = dao.xac_nhan_nhan_san(booking_id)

    if lich:
        flash(f'Đã xác nhận khách {lich.nguoi_dung.ho_ten} nhận sân!', 'success')
        return redirect(url_for('staff_bp.staff_dashboard', ngay=lich.ngay_choi))
    else:
        flash('Có lỗi xảy ra hoặc không tìm thấy lịch đặt này!', 'danger')
        return redirect(url_for('staff_bp.staff_dashboard'))


@staff_bp.route('/staff/my-history')
@login_required
def staff_history_view():
    ds_hoa_don = dao.get_lich_su_giao_dich(current_user.id)

    return render_template('staff/my_history.html', history=ds_hoa_don)
