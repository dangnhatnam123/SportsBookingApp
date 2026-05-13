from datetime import datetime

import flask
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app import models
from app.courts import courts_bp, dao
from app.utils import admin_required


@courts_bp.route('/')
def home():
    return render_template('main.html', LoaiSan=models.LoaiSan)


@courts_bp.route('/dieu-khoan')
def about():
    return render_template('dieu-khoan.html')


@courts_bp.route('/gioi-thieu')
def dieukhoan():
    return render_template('gioi-thieu.html')


@courts_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_view():
    err_msg = ''
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        avatar = request.files.get('avatar')

        if not name or not phone or not email:
            err_msg = "Vui lòng không để trống Họ tên, Email hoặc Số điện thoại!"
        else:
            try:
                dao.update_profile(current_user.id, name, phone, email, avatar)
                flash('Cập nhật thông tin cá nhân thành công!', 'success')
                return redirect(url_for('courts_bp.profile_view'))
            except Exception as ex:
                err_msg = str(ex)

    return render_template('profile.html', err_msg=err_msg)


@courts_bp.route('/admin/manage_san')
@login_required
@admin_required
def manage_san():
    try:
        danh_sach = dao.load_all_san()
    except Exception as e:
        print(f"Lỗi lấy dữ liệu: {e}")
        danh_sach = []
    return render_template('admin/manage_san.html', danh_sach_san=danh_sach)


@courts_bp.route('/admin/add-san', methods=['POST'])
def add_san():
    ten = request.form.get('ten_san')
    loai = request.form.get('loai_san')
    gia = float(request.form.get('gia'))

    if dao.check_ten_san(ten):
        flash(f"Tên sân '{ten}' đã tồn tại trong hệ thống!", "warning")
        return redirect(url_for('courts_bp.manage_san'))
    if gia <= 0:
        flash(f"giá sân '{gia}' không hợp lệ!", "warning")
        return redirect(url_for('courts_bp.manage_san'))
    try:
        dao.add_san_moi(ten, loai, gia)
        flash("Thêm sân thành công!", "success")
    except Exception as e:
        flash("thêm sân thất bại", "danger")

    return redirect(url_for('courts_bp.manage_san'))


@courts_bp.route('/admin/delete-san/<int:san_id>', methods=['POST'])
def delete_san(san_id):
    print(dao.kiem_tra_lich_dat(san_id))
    if dao.kiem_tra_lich_dat(san_id):
        flash("Sân đã có lịch đặt trong tương lai. Không thể xóa!", "danger")
    else:
        try:
            dao.xoa_san(san_id)
            flash("Đã xóa sân thành công!", "success")
        except Exception as e:
            flash(f"Lỗi hệ thống", "danger")
    return redirect(url_for('courts_bp.manage_san'))


@courts_bp.route('/admin/edit-san/<int:san_id>', methods=['POST'])
def edit_san(san_id):
    ten = request.form.get('ten_san')
    loai = request.form.get('loai_san')
    gia = float(request.form.get('gia'))

    if dao.check_ten_san(ten, exclude_id=san_id):
        flash(f"Lỗi: Tên sân '{ten}' đã được sử dụng!", "danger")
    else:
        if gia <= 0:
            flash(f"giá sân '{gia}' không hợp lệ!", "warning")
            return redirect(url_for('courts_bp.manage_san'))
        try:
            dao.update_san(san_id, ten, loai, gia)
            flash("Cập nhật thông tin sân thành công!", "success")
        except Exception as e:
            flash(f"Lỗi cập nhật: {e}", "danger")

    return redirect(url_for('courts_bp.manage_san'))
