from flask import render_template
from app import models
from app.courts import courts_bp


@courts_bp.route('/')
def home():
    return render_template('main.html', LoaiSan=models.LoaiSan)

@courts_bp.route('/dieu-khoan')
def about():
    return render_template('dieu-khoan.html')

@courts_bp.route('/gioi-thieu')
def dieukhoan():
    return render_template('gioi-thieu.html')