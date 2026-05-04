import math
from datetime import date, datetime, timedelta
import json
import uuid
import hmac
import hashlib
import requests

from flask import request, render_template, current_app, redirect, url_for, flash
from flask_login import login_required, current_user

from app import models
from app.booking import booking_bp, dao
from app.models import DatLich, VaiTro


@booking_bp.route('/san/<int:san_id>')
def court_detail(san_id):
    san = dao.get_san_by_id(san_id)
    if not san:
        return "Không tìm thấy sân này!", 404
    return render_template('detail_san.html', san=san)


@booking_bp.route('/search')
def booking_view():
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
        ngay = datetime.strptime(ngay_chon, '%Y-%m-%d').date()
        t1 = datetime.strptime(gio_bd, '%H:%M').time()
        t2 = datetime.strptime(gio_kt, '%H:%M').time()

        tong_phut_bd = t1.hour * 60 + t1.minute
        tong_phut_kt = t2.hour * 60 + t2.minute
        so_phut_choi = tong_phut_kt - tong_phut_bd

        if ngay < today:
            err_msg = "Lỗi: Không thể tìm sân trong quá khứ!"
        elif ngay == today and t1 < datetime.now().time():
            err_msg = "Lỗi: Vui lòng chọn giờ khác, không được chọn giờ trong quá khứ!"
        elif so_phut_choi <= 0:
            err_msg = "Lỗi: Giờ kết thúc phải lớn hơn giờ bắt đầu!"
        elif so_phut_choi < 60:
            err_msg = "Lỗi: Thời gian thuê tối thiểu phải là 1 tiếng!"

    if not err_msg:
        DS = dao.load_san_trong(loai_san_val=loai, ngay=ngay, gio_bd=t1, gio_kt=t2, page=page)
        total = dao.count_san_trong(loai_san_val=loai, ngay=ngay, gio_bd=t1, gio_kt=t2)
        if total > 0:
            pages = math.ceil(total / current_app.config.get('PAGE_SIZE', 6))

    return render_template('search.html', danh_sach_san=DS, pages=pages,
                           current_page=page, loai_san=loai, ngay=ngay_chon, gio_bd=gio_bd, gio_kt=gio_kt,
                           LoaiSan=models.LoaiSan, stats=dao.count_san_by_type(), today=today, err_msg=err_msg)


@booking_bp.route('/checkout/<int:san_id>')
@login_required
def checkout_view(san_id):
    ngay = request.args.get('ngay')
    gio_bd = request.args.get('gio_bd')
    gio_kt = request.args.get('gio_kt')

    if not ngay or not gio_bd or not gio_kt:
        return redirect(url_for('booking_bp.booking_view'))

    san = dao.get_san_by_id(san_id)
    if not san:
        return redirect(url_for('booking_bp.booking_view'))

    soluongsandat = dao.count_dat_san_trong_ngay(current_user.id, ngay)
    if current_user.vai_tro == VaiTro.NGUOI_DUNG and soluongsandat >= 3:
        return render_template('error_book_san.html', ngay=ngay)

    fmt = '%H:%M'
    t1 = datetime.strptime(gio_bd, fmt)
    t2 = datetime.strptime(gio_kt, fmt)
    tong_gio = (t2 - t1).total_seconds() / 3600
    tong_tien = tong_gio * san.gia_san_theo_gio

    return render_template('checkout.html', san=san, ngay=ngay, gio_bd=gio_bd,
                           gio_kt=gio_kt, tong_gio=tong_gio, tong_tien=tong_tien)


@booking_bp.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    san_id = request.form.get('san_id')
    ngay = request.form.get('ngay')
    gio_bd = request.form.get('gio_bd')
    gio_kt = request.form.get('gio_kt')
    tong_tien = request.form.get('tong_tien')
    payment_method = request.form.get('payment_method')

    san_obj = dao.get_san_by_id(san_id)
    ten_san = san_obj.ten_san if san_obj else f"Sân #{san_id}"

    fmt = '%H:%M'
    t1 = datetime.strptime(gio_bd, fmt)
    t2 = datetime.strptime(gio_kt, fmt)
    so_gio = (t2 - t1).total_seconds() / 3600

    new_booking = dao.luu_dat_san(
        ma_nd=current_user.id, ma_san=san_id, ngay_choi=ngay,
        gio_bd=gio_bd, gio_kt=gio_kt, tong_tien=tong_tien, loai_thanh_toan=payment_method
    )

    if new_booking:
        if payment_method == 'momo':
            endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
            partnerCode, accessKey, secretKey = "MOMO", "F8BBA842ECF85", "K951B6PE1waDMi640xX08PD3vg6EkVlz"
            orderId = f"BILL_{new_booking.id}_{str(uuid.uuid4())[:8]}"
            requestId = str(uuid.uuid4())
            orderInfo = f"{ten_san} | {so_gio}h | {ngay}"
            redirectUrl = url_for('booking_bp.history_view', _external=True)
            ipnUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
            amount = str(int(float(tong_tien)))

            rawSignature = f"accessKey={accessKey}&amount={amount}&extraData=&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}&redirectUrl={redirectUrl}&requestId={requestId}&requestType=captureWallet"
            signature = hmac.new(bytes(secretKey, 'utf-8'), bytes(rawSignature, 'utf-8'), hashlib.sha256).hexdigest()

            data = {
                'partnerCode': partnerCode, 'partnerName': "Sports Booking App", 'storeId': "MomoTestStore",
                'requestId': requestId, 'amount': amount, 'orderId': orderId, 'orderInfo': orderInfo,
                'redirectUrl': redirectUrl, 'ipnUrl': ipnUrl, 'lang': "vi", 'extraData': "",
                'requestType': "captureWallet", 'signature': signature
            }

            try:
                response = requests.post(endpoint, data=json.dumps(data), headers={'Content-Type': 'application/json'})
                res_json = response.json()
                if 'payUrl' in res_json:
                    return redirect(res_json['payUrl'])
                else:
                    dao.xoa_don_loi(new_booking.id)
                    flash('Lỗi cổng thanh toán MoMo, đơn hàng đã bị hủy!', 'danger')
                    return redirect(url_for('booking_bp.booking_view'))
            except Exception as e:
                dao.xoa_don_loi(new_booking.id)
                flash(f'Không thể kết nối MoMo: {e}', 'danger')
                return redirect(url_for('booking_bp.booking_view'))

        flash('Đặt sân thành công!', 'success')
        return redirect(url_for('booking_bp.history_view'))

    flash('Có lỗi xảy ra khi lưu đơn hàng!', 'danger')
    return redirect(url_for('booking_bp.booking_view'))


@booking_bp.route('/orders')
@login_required
def history_view():
    momo_trans_id = request.args.get('transId')
    order_id_full = request.args.get('orderId')
    result_code = request.args.get('resultCode')

    # Nếu thanh toán thất bại hoặc hủy trên trang MoMo
    if result_code and result_code != '0' and order_id_full:
        try:
            ma_dat_san = order_id_full.split('_')[1]
            dao.xoa_don_loi(ma_dat_san)
            flash('Thanh toán không thành công, đơn hàng đã bị hủy.', 'warning')
        except:
            pass

    # Nếu thanh toán thành công -> Cập nhật mã giao dịch thật
    elif result_code == '0' and momo_trans_id and order_id_full:
        try:
            ma_dat_san = order_id_full.split('_')[1]
            dao.update_momo_trans_id(ma_dat_san, momo_trans_id)
        except:
            pass

    page = request.args.get('page', 1, type=int)
    history_list, total_pages = dao.get_history_by_user(current_user.id, page=page)
    return render_template('history.html', history=history_list, pages=total_pages,
                           current_page=page, now=datetime.now(), datetime=datetime)


@booking_bp.route('/huy-dat-san/<int:ma_dat_san>', methods=['POST'])
@login_required
def process_huy_dat(ma_dat_san):
    PARTNER_CODE, ACCESS_KEY, SECRET_KEY = "MOMO", "F8BBA842ECF85", "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    REFUND_ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/refund"

    dat_lich = DatLich.query.get_or_404(ma_dat_san)

    if dat_lich.ma_nd != current_user.id:
        flash('Lỗi: Bạn không có quyền hủy đơn này!', 'danger')
        return redirect(url_for('booking_bp.history_view'))

    if dat_lich.trang_thai_hien_tai == 'Sân đang được sử dụng':
        flash('Lỗi: Sân đang chơi, không thể hủy!', 'danger')
        return redirect(url_for('booking_bp.history_view'))

    now = datetime.now()
    thoi_gian_bat_dau = datetime.combine(dat_lich.ngay_choi, dat_lich.gio_bd)
    if now >= thoi_gian_bat_dau or (thoi_gian_bat_dau - now) < timedelta(hours=2):
        flash('Lỗi: Chỉ được hủy trước giờ chơi ít nhất 2 tiếng!', 'danger')
        return redirect(url_for('booking_bp.history_view'))

    if dat_lich.loai_thanh_toan == 'momo':
        trans_id = getattr(dat_lich, 'momo_trans_id', None)
        if trans_id:
            if trans_id.startswith("MOMO_TEST"):
                if dao.huy_dat_san(ma_dat_san):
                    flash('Đã hủy đơn test thành công!', 'success')
                    return redirect(url_for('booking_bp.history_view'))

            order_id = f"REFUND_{ma_dat_san}_{str(uuid.uuid4())[:8]}"
            request_id = str(uuid.uuid4())
            amount = str(int(float(dat_lich.hoa_don.tong_tien)))
            description = f"Hoan tien san #{ma_dat_san}"

            raw_sig = f"accessKey={ACCESS_KEY}&amount={amount}&description={description}&orderId={order_id}&partnerCode={PARTNER_CODE}&requestId={request_id}&transId={trans_id}"
            signature = hmac.new(bytes(SECRET_KEY, 'utf-8'), bytes(raw_sig, 'utf-8'), hashlib.sha256).hexdigest()

            try:
                res = requests.post(REFUND_ENDPOINT, data=json.dumps({
                    'partnerCode': PARTNER_CODE, 'orderId': order_id, 'requestId': request_id,
                    'amount': amount, 'transId': trans_id, 'description': description,
                    'signature': signature, 'lang': 'vi'
                }), headers={'Content-Type': 'application/json'})
                if res.json().get('resultCode') != 0:
                    flash(f"Lỗi MoMo: {res.json().get('message')}", 'warning')
                    return redirect(url_for('booking_bp.history_view'))
            except Exception as e:
                flash(f"Lỗi kết nối hoàn tiền: {e}", 'danger')
                return redirect(url_for('booking_bp.history_view'))
        else:
            flash('Không tìm thấy mã giao dịch MoMo!', 'warning')
            return redirect(url_for('booking_bp.history_view'))

    if dao.huy_dat_san(ma_dat_san):
        flash('Hủy đặt sân thành công!', 'success')
    else:
        flash('Có lỗi xảy ra khi hủy!', 'danger')
    return redirect(url_for('booking_bp.history_view'))