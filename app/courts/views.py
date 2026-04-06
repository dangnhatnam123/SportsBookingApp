from flask import render_template, request, flash, redirect, url_for
from app import models
from app.courts import courts_bp, dao


@courts_bp.route('/')
def home():
    return render_template('main.html', LoaiSan=models.LoaiSan)

@courts_bp.route('/dieu-khoan')
def about():
    return render_template('dieu-khoan.html')

@courts_bp.route('/gioi-thieu')
def dieukhoan():
    return render_template('gioi-thieu.html')

@courts_bp.route('/admin/manage_san')
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
    gia = request.form.get('gia')

    try:
        dao.add_san_moi(ten,loai,gia)
        flash("Thêm sân thành công!")
    except Exception as e:
        flash("thêm sân thất bại")

    return redirect(url_for('courts_bp.manage_san'))


