import pytest
from unittest.mock import patch, MagicMock
from app.booking.dao import update_momo_trans_id
from app.models import DatLich
from test.test_base import test_app, test_session

def test_update_momo_success(test_app, test_session):
    with patch('app.models.DatLich.query') as mock_query:
        mock_dl = MagicMock()
        mock_query.get.return_value = mock_dl

        with patch('app.db.session.commit') as mock_commit:
            result = update_momo_trans_id(ma_dat_san=1, trans_id="MOMO_123456")

            assert result is True
            assert mock_dl.momo_trans_id == "MOMO_123456"
            mock_commit.assert_called_once()

def test_update_momo_id_not_found(test_app, test_session):
    with patch('app.models.DatLich.query') as mock_query:
        mock_query.get.return_value = None

        result = update_momo_trans_id(ma_dat_san=999, trans_id="MOMO_ERROR")

        assert result is False

def test_update_momo_db_error(test_app, test_session):
    with patch('app.models.DatLich.query') as mock_query:
        mock_dl = MagicMock()
        mock_query.get.return_value = mock_dl

        with patch('app.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database rớt mạng!")

            with pytest.raises(Exception):
                update_momo_trans_id(ma_dat_san=1, trans_id="MOMO_FAIL")