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


function previewAvatar(input) {
    const fileName = document.getElementById('file-name');
    const previewImg = document.getElementById('preview-img');

    if (input.files && input.files[0]) {
        fileName.textContent = input.files[0].name;
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImg.src = e.target.result;
        }
        reader.readAsDataURL(input.files[0]);
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


function checkLogin(event) {
    event.preventDefault();
    alert("Vui lòng đăng nhập để thực hiện đặt sân!");
    window.location.href = "/login";
}