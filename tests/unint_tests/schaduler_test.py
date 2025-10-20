import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from schaduler import scheduled_messages


@pytest.mark.asyncio
async def test_scheduled_messages_calls_prayer_ahd(monkeypatch):
    """تست: وقتی ساعت 06:00 است، تابع send_prayer('ahd') اجرا شود"""

    # --- زمان جعلی ---
    class FakeDatetime:
        @staticmethod
        def now(tz=None):
            from datetime import datetime
            return datetime(2024, 1, 1, 6, 0, 0)

    monkeypatch.setattr("schaduler.datetime", FakeDatetime)

    # --- Mock وابستگی‌ها ---
    mock_send_prayer = AsyncMock()
    mock_get_state = MagicMock(return_value=True)
    mock_sleep = AsyncMock(side_effect=Exception("stop"))  # برای توقف حلقه بی‌نهایت

    monkeypatch.setattr("schaduler.get_schaduler_state", mock_get_state)
    monkeypatch.setattr("schaduler.general_services", MagicMock(send_prayer=mock_send_prayer))
    monkeypatch.setattr("schaduler.asyncio.sleep", mock_sleep)

    # --- اجرا ---
    try:
        await scheduled_messages()
    except Exception as e:
        assert str(e) == "stop"

    # --- انتظار ---
    mock_send_prayer.assert_awaited_once_with("ahd")


@pytest.mark.asyncio
async def test_scheduled_messages_handles_exception(monkeypatch):
    """تست: وقتی یکی از تسک‌ها خطا می‌دهد، send_to_admins فراخوانی شود"""

    # --- زمان جعلی ---
    class FakeDatetime:
        @staticmethod
        def now(tz=None):
            from datetime import datetime
            return datetime(2024, 1, 1, 9, 34, 0)

    monkeypatch.setattr("schaduler.datetime", FakeDatetime)

    # --- Mock سرویس‌ها ---
    mock_hadith = AsyncMock(side_effect=Exception("test error"))
    mock_send_to_admins = AsyncMock()
    mock_get_state = MagicMock(return_value=True)
    mock_sleep = AsyncMock(side_effect=Exception("stop"))

    monkeypatch.setattr("schaduler.hadith_services", MagicMock(auto_send=mock_hadith))
    monkeypatch.setattr("schaduler.send_to_admins", mock_send_to_admins)
    monkeypatch.setattr("schaduler.get_schaduler_state", mock_get_state)
    monkeypatch.setattr("schaduler.asyncio.sleep", mock_sleep)

    # --- اجرا ---
    try:
        await scheduled_messages()
    except Exception as e:
        assert str(e) == "stop"

    # --- انتظار ---
    mock_send_to_admins.assert_awaited_once()
    called_message = mock_send_to_admins.call_args[0][0]
    assert "خطا" in called_message
    assert "09:34" in called_message


@pytest.mark.asyncio
async def test_scheduled_messages_does_nothing_when_state_off(monkeypatch):
    """تست: وقتی get_schaduler_state=False هیچ تسکی اجرا نشود"""

    class FakeDatetime:
        @staticmethod
        def now(tz=None):
            from datetime import datetime
            return datetime(2024, 1, 1, 6, 0, 0)

    monkeypatch.setattr("schaduler.datetime", FakeDatetime)

    mock_get_state = MagicMock(return_value=False)
    mock_send_prayer = AsyncMock()
    mock_sleep = AsyncMock(side_effect=Exception("stop"))

    monkeypatch.setattr("schaduler.get_schaduler_state", mock_get_state)
    monkeypatch.setattr("schaduler.general_services", MagicMock(send_prayer=mock_send_prayer))
    monkeypatch.setattr("schaduler.asyncio.sleep", mock_sleep)

    try:
        await scheduled_messages()
    except Exception as e:
        assert str(e) == "stop"

    # چون scheduler خاموش است، نباید هیچ فراخوانی شده باشد
    mock_send_prayer.assert_not_called()
