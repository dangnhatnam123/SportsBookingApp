import math
from datetime import date, datetime, timedelta

from flask import request, render_template, current_app, redirect, url_for, flash
from flask_login import login_required, current_user

from app import models
from app.booking import booking_bp, dao
from app.models import DatLich, VaiTro

import json
import uuid
import hmac
import hashlib
import requests

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
            err_msg = "Lỗi: Vui lòng chọn giờ khác, không được chọn giờ tỏng quá khứ!"
        elif so_phut_choi <= 0:
            err_msg = "Lỗi: Giờ kết thúc phải lớn hơn giờ bắt đầu!"
        elif so_phut_choi < 60:
            err_msg = "Lỗi: Thời gian thuê tối thiểu phải là 1 tiếng!"


    if not err_msg:
        DS = dao.load_san_trong(loai_san_val=loai, ngay=ngay, gio_bd=t1, gio_kt=t2, page=page)
        total = dao.count_san_trong(loai_san_val=loai, ngay=ngay, gio_bd=t1, gio_kt=t2)

        if total > 0:
            pages = math.ceil(total / current_app.config.get('PAGE_SIZE', 6))

    return render_template('search.html',danh_sach_san=DS,pages=pages,
                           current_page=page, loai_san=loai, ngay=ngay_chon, gio_bd=gio_bd, gio_kt=gio_kt,
                           LoaiSan=models.LoaiSan,stats=dao.count_san_by_type(),today=today,err_msg=err_msg)



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

    soluongsandat = dao.count_dat_san_trong_ngay(current_user.id,ngay)
    if current_user.vai_tro == VaiTro.NGUOI_DUNG:
        if soluongsandat >= 3:
            return render_template('error_book_san.html', ngay=ngay)

    san = dao.get_san_by_id(san_id)
    if not san:
        return redirect(url_for('booking_bp.booking_view'))

    fmt = '%H:%M'
    t1 = datetime.strptime(gio_bd, fmt)
    t2 = datetime.strptime(gio_kt, fmt)
    tong_gio = (t2 - t1).total_seconds() / 3600
    tong_tien = tong_gio * san.gia_san_theo_gio

    return render_template('checkout.html',
                           san=san, ngay=ngay, gio_bd=gio_bd,
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

    # --- BƯỚC MỚI: Lấy thông tin sân và tính số giờ để hiện lên MoMo ---
    san_obj = dao.get_san_by_id(san_id)
    ten_san = san_obj.ten_san if san_obj else f"Sân #{san_id}"

    fmt = '%H:%M'
    t1 = datetime.strptime(gio_bd, fmt)
    t2 = datetime.strptime(gio_kt, fmt)
    so_gio = (t2 - t1).total_seconds() / 3600
    new_booking = dao.luu_dat_san(
        ma_nd=current_user.id,
        ma_san=san_id,
        ngay_choi=ngay,
        gio_bd=gio_bd,
        gio_kt=gio_kt,
        tong_tien=tong_tien,
        loai_thanh_toan=payment_method
    )

    if new_booking:
        if payment_method == 'momo':
            endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
            partnerCode = "MOMO"
            accessKey = "F8BBA842ECF85"
            secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"

            orderId = f"BILL_{new_booking.id}_{str(uuid.uuid4())[:8]}"
            requestId = str(uuid.uuid4())

            # SỬA CHỖ NÀY: Nội dung hiển thị chi tiết cho người dùng kiểm tra
            orderInfo = f"{ten_san} | {so_gio}h | {ngay}"

            redirectUrl = url_for('booking_bp.history_view', _external=True)
            ipnUrl = "https://webhook.site/b3088a6a-2d17-4f8d-a383-71389a6c600b"
            requestType = "captureWallet"
            extraData = ""

            amount = str(int(float(tong_tien)))

            rawSignature = f"accessKey={accessKey}&amount={amount}&extraData={extraData}&ipnUrl={ipnUrl}&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}&redirectUrl={redirectUrl}&requestId={requestId}&requestType={requestType}"

            h = hmac.new(bytes(secretKey, 'utf-8'), bytes(rawSignature, 'utf-8'), hashlib.sha256)
            signature = h.hexdigest()

            data = {
                'partnerCode': partnerCode,
                'partnerName': "Sports Booking App",
                'storeId': "MomoTestStore",
                'requestId': requestId,
                'amount': amount,
                'orderId': orderId,
                'orderInfo': orderInfo,
                'redirectUrl': redirectUrl,
                'ipnUrl': ipnUrl,
                'lang': "vi",
                'extraData': extraData,
                'requestType': requestType,
                'signature': signature
            }

            try:
                response = requests.post(endpoint, data=json.dumps(data), headers={'Content-Type': 'application/json'})
                res_json = response.json()
                if 'payUrl' in res_json:
                    return redirect(res_json['payUrl'])
            except Exception as e:
                print(f"Lỗi gọi MoMo: {e}")

        flash('Đặt sân thành công!', 'success')
        return redirect(url_for('booking_bp.history_view'))

    else:
        flash('Có lỗi xảy ra khi lưu đơn hàng, vui lòng thử lại!', 'danger')
        return redirect(url_for('booking_bp.booking_view'))

@booking_bp.route('/orders')
@login_required
def history_view():
    momo_trans_id = request.args.get('transId')
    order_id_full = request.args.get('orderId') # Có dạng BILL_ID_xxxx
    result_code = request.args.get('resultCode')

    if result_code == '0' and momo_trans_id and order_id_full:
        try:
            ma_dat_san = order_id_full.split('_')[1]
            dao.update_momo_trans_id(ma_dat_san, momo_trans_id)
        except Exception as e:
            print(f"Lỗi cập nhật transId thật: {e}")

    page = request.args.get('page', 1, type=int)
    history_list, total_pages = dao.get_history_by_user(current_user.id, page=page)
    now = datetime.now()

    return render_template('history.html', history=history_list, pages=total_pages,
                           current_page=page, now=now, datetime=datetime)
@booking_bp.route('/huy-dat-san/<int:ma_dat_san>', methods=['POST'])
@login_required
def process_huy_dat(ma_dat_san):
    PARTNER_CODE = "MOMO"
    ACCESS_KEY = "F8BBA842ECF85"
    SECRET_KEY = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    REFUND_ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/refund"

    dat_lich = DatLich.query.get_or_404(ma_dat_san)

    # Ràng buộc 2.1
    if dat_lich.ma_nd != current_user.id:
        flash('Lỗi: Bạn không có quyền hủy lịch đặt sân của người khác!', 'danger')
        return redirect(url_for('booking_bp.history_view'))

    # Ràng buộc 2.3
    if dat_lich.trang_thai_hien_tai == 'Sân đang được sử dụng':
        flash('Lỗi: Sân đang có người chơi, không thể hủy!', 'danger')
        return redirect(url_for('booking_bp.history_view'))

    # Ràng buộc 2.2
    now = datetime.now()
    thoi_gian_bat_dau = datetime.combine(dat_lich.ngay_choi, dat_lich.gio_bd)
    if now >= thoi_gian_bat_dau:
        flash('Lỗi: Đã tới hoặc qua giờ nhận sân, bạn không thể hủy đơn này!', 'danger')
        return redirect(url_for('booking_bp.history_view'))

    thoi_gian_con_lai = thoi_gian_bat_dau - now
    if thoi_gian_con_lai < timedelta(hours=2):
        flash('Lỗi: Bạn chỉ được phép hủy sân trước giờ chơi ít nhất 2 tiếng!', 'danger')
        return redirect(url_for('booking_bp.history_view'))

    if dat_lich.loai_thanh_toan == 'momo':
        # Bà nhớ đảm bảo đã lưu transId vào cột momo_trans_id lúc thanh toán nhé
        trans_id = getattr(dat_lich, 'momo_trans_id', None)

        if trans_id:
            if trans_id.startswith("MOMO_TEST"):
                if dao.huy_dat_san(ma_dat_san):
                    flash('Đã hủy đơn test thành công (Không gọi MoMo vì mã giả)!', 'success')
                    return redirect(url_for('booking_bp.history_view'))
            order_id = f"REFUND_{ma_dat_san}_{str(uuid.uuid4())[:8]}"
            request_id = str(uuid.uuid4())
            amount = str(int(float(dat_lich.hoa_don.tong_tien)))
            description = f"Hoan tien san #{ma_dat_san}"

            raw_sig = f"accessKey={ACCESS_KEY}&amount={amount}&description={description}&orderId={order_id}&partnerCode={PARTNER_CODE}&requestId={request_id}&transId={trans_id}"
            h = hmac.new(bytes(SECRET_KEY, 'utf-8'), bytes(raw_sig, 'utf-8'), hashlib.sha256)
            signature = h.hexdigest()

            refund_data = {
                'partnerCode': PARTNER_CODE,
                'orderId': order_id,
                'requestId': request_id,
                'amount': amount,
                'transId': trans_id,
                'description': description,
                'signature': signature,
                'lang': 'vi'
            }

            try:
                res = requests.post(REFUND_ENDPOINT, data=json.dumps(refund_data),
                                    headers={'Content-Type': 'application/json'})
                res_json = res.json()

                if res_json.get('resultCode') != 0:
                    flash(f"Lỗi hoàn tiền MoMo: {res_json.get('message')}", 'warning')
                    return redirect(url_for('booking_bp.history_view'))
            except Exception as e:
                flash(f"Không thể kết nối MoMo để hoàn tiền: {e}", 'danger')
                return redirect(url_for('booking_bp.history_view'))
        else:
            flash('Không tìm thấy mã giao dịch MoMo để hoàn tiền tự động!', 'warning')
            return redirect(url_for('booking_bp.history_view'))

    if dao.huy_dat_san(ma_dat_san):
        flash('Hủy đặt sân thành công!', 'success')
    else:
        flash('Có lỗi xảy ra khi hủy đặt sân trên hệ thống!', 'danger')

    return redirect(url_for('booking_bp.history_view'))
