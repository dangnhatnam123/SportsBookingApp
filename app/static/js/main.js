document.addEventListener("DOMContentLoaded", function() {
    // 1. Lấy đường dẫn hiện tại trên thanh địa chỉ (ví dụ: / hoặc /gioi-thieu)
    let currentPath = window.location.pathname;

    // 2. Gom tất cả các đường link trong thanh menu lại
    let menuLinks = document.querySelectorAll('.main-menu a, .right-menu a');

    // 3. Cho code chạy qua từng cái link một
    menuLinks.forEach(link => {
        // Lấy cái đích đến của link đó (href)
        let linkPath = link.getAttribute('href');

        // Nếu đích đến khớp với trang hiện tại -> Bật đèn vàng (thêm class active)
        if (linkPath === currentPath) {
            link.classList.add('active');
        }
    });
});