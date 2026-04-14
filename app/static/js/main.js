function nhacNhoChonGio() {
    alert("Vui lòng chọn Ngày chơi và Giờ chơi ở bảng tìm kiếm phía trên trước khi đặt sân nhé!");
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
    const ngayInput = document.querySelector('input[name="ngay"]');
    if (ngayInput) {
        ngayInput.focus();
        ngayInput.style.outline = "3px solid #ffc107";
        setTimeout(() => { ngayInput.style.outline = ""; }, 2000);
    }
}

document.addEventListener("DOMContentLoaded", function() {
        const qrArea = document.getElementById('momo-qr-area');
        const radios = document.querySelectorAll('.payment-method-radio');

        radios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'cash') {
                    qrArea.style.display = 'none';
                } else {
                    qrArea.style.display = 'block';
                }
            });
        });
    });


