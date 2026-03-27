//document.addEventListener("DOMContentLoaded", function() {
//    // 1. Lấy đường dẫn hiện tại trên thanh địa chỉ (ví dụ: / hoặc /gioi-thieu)
//    let currentPath = window.location.pathname;
//
//    // 2. Gom tất cả các đường link trong thanh menu lại
//    let menuLinks = document.querySelectorAll('.main-menu a, .right-menu a');
//
//    // 3. Cho code chạy qua từng cái link một
//    menuLinks.forEach(link => {
//        // Lấy cái đích đến của link đó (href)
//        let linkPath = link.getAttribute('href');
//
//        // Nếu đích đến khớp với trang hiện tại -> Bật đèn vàng (thêm class active)
//        if (linkPath === currentPath) {
//            link.classList.add('active');
//        }
//    });
//});
//
//document.querySelector('.search-bar-main').addEventListener('submit', function(e) {
//    // Lấy giá trị giờ mà khách chọn
//    let gioBD = document.getElementById('gio_bat_dau').value;
//    let gioKT = document.getElementById('gio_ket_thuc').value;
//
//    if (gioBD && gioKT) {
//        // Chuyển đổi giờ thành số phút để dễ tính toán (VD: 17:30 -> 17*60 + 30)
//        let phutBD = parseInt(gioBD.split(':')[0]) * 60 + parseInt(gioBD.split(':')[1]);
//        let phutKT = parseInt(gioKT.split(':')[0]) * 60 + parseInt(gioKT.split(':')[1]);
//
//        // Kiểm tra ràng buộc: Giờ kết thúc phải lớn hơn Giờ bắt đầu
//        if (phutKT <= phutBD) {
//            e.preventDefault(); // Chặn không cho gửi form
//            alert('Lỗi: Giờ kết thúc phải lớn hơn giờ bắt đầu!');
//            return;
//        }
//
//        // Kiểm tra ràng buộc của Đề tài: Tối thiểu 1 giờ (60 phút)
//        if (phutKT - phutBD < 60) {
//            e.preventDefault();
//            alert('Theo quy định: Bạn phải đặt sân tối thiểu 1 giờ!');
//            return;
//        }
//    }
//});
