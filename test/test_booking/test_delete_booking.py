# import pytest
# from unittest.mock import patch, MagicMock
# from app.booking.dao import xoa_don_loi
# from app.models import DatLich
# from test.test_base import test_app, test_session
#
# # Đường dẫn patch cần trỏ thẳng vào file dao.py nơi DatLich được sử dụng
# PATCH_PATH = 'app.booking.dao.DatLich.query.get'
#
#
# def test_xoa_don_loi_co_hoa_don_success(test_app, test_session):
#     mock_don_hang = MagicMock(spec=DatLich)
#     mock_hoa_don = MagicMock()
#     mock_don_hang.hoa_don = mock_hoa_don
#
#     with patch(PATCH_PATH, return_value=mock_don_hang), \
#             patch('app.booking.dao.db.session.delete') as mock_delete, \
#             patch('app.booking.dao.db.session.commit') as mock_commit:
#         result = xoa_don_loi(ma_dat_san=10)
#
#         assert result is True
#         assert mock_delete.call_count == 2
#         mock_commit.assert_called_once()
#
#
# def test_xoa_don_loi_khong_hoa_don_success(test_app, test_session):
#     mock_don_hang = MagicMock(spec=DatLich)
#     mock_don_hang.hoa_don = None
#
#     with patch(PATCH_PATH, return_value=mock_don_hang), \
#             patch('app.booking.dao.db.session.delete') as mock_delete, \
#             patch('app.booking.dao.db.session.commit') as mock_commit:
#         result = xoa_don_loi(ma_dat_san=11)
#
#         assert result is True
#         mock_delete.assert_called_once_with(mock_don_hang)
#         mock_commit.assert_called_once()
#
#
# def test_xoa_don_loi_not_found(test_app, test_session):
#     with patch(PATCH_PATH, return_value=None):
#         result = xoa_don_loi(ma_dat_san=999)
#         assert result is False
#
#
# def test_xoa_don_loi_db_error(test_app, test_session):
#     mock_don_hang = MagicMock(spec=DatLich)
#
#     # Ở đây chúng ta patch db ngay tại file dao để chắc chắn bắt được Exception
#     with patch(PATCH_PATH, return_value=mock_don_hang), \
#             patch('app.booking.dao.db.session.delete'), \
#             patch('app.booking.dao.db.session.commit', side_effect=Exception("Lỗi Database")):
#         with pytest.raises(Exception):
#             xoa_don_loi(ma_dat_san=10)