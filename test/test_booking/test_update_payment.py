import pytest
from unittest.mock import patch, MagicMock
from app.booking.dao import cap_nhat_thanh_toan_thanh_cong
from app.models import DatLich, HoaDon, TrangThaiHoaDon
from test.test_base import test_app, test_session

def test_update_payment_success(test_app, test_session):
    with patch('app.models.DatLich.query') as mock_query:
        mock_dl = MagicMock()
        mock_hd = MagicMock()
        mock_dl.hoa_don = mock_hd
        mock_query.get.return_value = mock_dl

        with patch('app.db.session.commit') as mock_commit:
            result = cap_nhat_thanh_toan_thanh_cong(ma_dat_san=1, trans_id="MOMO123")

            assert result is True
            assert mock_dl.momo_trans_id == "MOMO123"
            assert mock_hd.trang_thai == TrangThaiHoaDon.DA_THANH_TOAN
            mock_commit.assert_called_once()

def test_update_payment_id_not_found(test_app, test_session):
    with patch('app.models.DatLich.query') as mock_query:
        mock_query.get.return_value = None

        result = cap_nhat_thanh_toan_thanh_cong(ma_dat_san=9999)

        assert result is False

def test_update_payment_db_error(test_app, test_session):
    with patch('app.models.DatLich.query') as mock_query:
        mock_dl = MagicMock()
        mock_query.get.return_value = mock_dl

        with patch('app.db.session.commit') as mock_commit:
            with patch('app.db.session.rollback') as mock_rollback:
                mock_commit.side_effect = Exception("Lỗi kết nối database")

                result = cap_nhat_thanh_toan_thanh_cong(ma_dat_san=1)

                assert result is False
                mock_rollback.assert_called_once()