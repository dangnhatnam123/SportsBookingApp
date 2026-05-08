import pytest
from unittest.mock import patch, MagicMock
from app.booking.dao import xoa_don_loi

def test_xoa_don_loi_co_hoa_don_success():
    mock_don_hang = MagicMock()
    mock_hoa_don = MagicMock()
    mock_don_hang.hoa_don = mock_hoa_don

    with patch('app.booking.dao.DatLich') as mock_datlich_class, \
            patch('app.booking.dao.db.session.delete') as mock_delete, \
            patch('app.booking.dao.db.session.commit') as mock_commit:
        mock_datlich_class.query.get.return_value = mock_don_hang
        result = xoa_don_loi(ma_dat_san=10)

        assert result is True
        assert mock_delete.call_count == 2
        mock_commit.assert_called_once()

def test_xoa_don_loi_khong_hoa_don_success():
    mock_don_hang = MagicMock()
    mock_don_hang.hoa_don = None

    with patch('app.booking.dao.DatLich') as mock_datlich_class, \
            patch('app.booking.dao.db.session.delete') as mock_delete, \
            patch('app.booking.dao.db.session.commit') as mock_commit:
        mock_datlich_class.query.get.return_value = mock_don_hang
        result = xoa_don_loi(ma_dat_san=11)

        assert result is True
        mock_delete.assert_called_once_with(mock_don_hang)
        mock_commit.assert_called_once()

def test_xoa_don_loi_not_found():
    with patch('app.booking.dao.DatLich') as mock_datlich_class:
        mock_datlich_class.query.get.return_value = None
        result = xoa_don_loi(ma_dat_san=999)
        assert result is False

def test_xoa_don_loi_db_error():
    mock_don_hang = MagicMock()
    with patch('app.booking.dao.DatLich') as mock_datlich_class, \
            patch('app.booking.dao.db.session.delete'), \
            patch('app.booking.dao.db.session.commit') as mock_commit:
        mock_datlich_class.query.get.return_value = mock_don_hang
        mock_commit.side_effect = Exception("Lỗi kết nối Database")

        with pytest.raises(Exception):
            xoa_don_loi(ma_dat_san=10)