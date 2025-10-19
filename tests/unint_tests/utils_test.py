# tests/utils_tests/test_datetime_utils.py
import pytest
import io
import asyncio
import json
from unittest.mock import patch, AsyncMock, MagicMock, mock_open
from utils.media import file_id_to_bynery, get_media_bytes
from utils.datetime import get_mentioning_day
from utils.notifiter import send_to_admins
from utils.response import success_response, error_response
from utils.text_utils import (
    split_text_with_index,
    fa_to_en_int,
    prepare_processed_messages,
)
from utils.decorator import safe_run  # مسیر درست ایمپورت را تنظیم کن
from utils.keyboard import (
    main_menu,
    message_menu,
    audios_menu,
    note_menu,
    schaduler_menu,
    book_menu,
    save_or_edit_menu,
    send_menu,
    answer_y_n,
    edit_note_menu,
    back_menu,
)


#! utils.keyboard is ignored

#! utils.message_prosseccing is ignored


@pytest.fixture(autouse=True)
def mock_base_url(monkeypatch):
    """
    مقدار base_mentioning_image_url را برای تست به یک مسیر ویندوزی ست می‌کنیم.
    این مقدارِ تستی فقط برای بررسی ساختار رشته مسیر مورد استفاده قرار می‌گیرد
    (نیازی به وجود واقعی فایل/فولدر نیست).
    """
    windows_path = r"C:/projects/mybot/assets/images/zekr_day"
    monkeypatch.setattr("utils.datetime.base_mentioning_image_url", windows_path)


@pytest.mark.parametrize(
    "day_en, expected_fa, expected_zekr, image_index",
    [
        ("Saturday", "شنبه", "یا رب العالمین", 1),
        ("Sunday", "یک‌شنبه", "یا ذاالجلال و الاکرام", 2),
        ("Monday", "دوشنبه", "یا قاضی الحاجات", 3),
        ("Tuesday", "سه‌شنبه", "یا ارحم الراحمین", 4),
        ("Wednesday", "چهارشنبه", "یا حی یا قیوم", 5),
        ("Thursday", "پنج‌شنبه", "لا اله الا الله الملک الحق المبین", 6),
        ("Friday", "جمعه", "اللهم صل علی محمد و آل محمد", 7),
    ],
)
def test_get_mentioning_day_valid_days(day_en, expected_fa, expected_zekr, image_index):
    """
    برای هر روز هفته چک می‌کنیم که:
    - نام فارسی (fa) درست باشد
    - ذکر (zekr) درست باشد
    - تاریخ جلالی به فرمت YYYY/MM/DD بازگشت شده باشد
    - مسیر تصویر مطابق base_mentioning_image_url ساخته شده باشد (با شماره صحیح)
    """
    fake_jalali_date = "1404/01/01"

    # patch کردن datetime و jdatetime در فضای نام utils.datetime_utils
    with patch("utils.datetime.datetime") as mock_datetime, patch(
        "utils.datetime.jdatetime.datetime"
    ) as mock_jdatetime:

        # datetime.now().strftime("%A") باید day_en برگرداند
        mock_now = mock_datetime.now.return_value
        mock_now.strftime.return_value = day_en

        # jdatetime.datetime.now().strftime(...) باید تاریخ شمسی برگرداند
        mock_jnow = mock_jdatetime.now.return_value
        mock_jnow.strftime.return_value = fake_jalali_date

        result = get_mentioning_day()

        assert isinstance(result, dict)
        assert result["name"] == expected_fa
        assert result["zekr"] == expected_zekr
        assert result["date"] == fake_jalali_date

        # چون base_mentioning_image_url یک مسیر ویندوزی است، خروجی باید مثل:
        # C:/projects/mybot/assets/images/zekr_day (1).jpg
        expected_path = rf"C:/projects/mybot/assets/images/zekr_day ({image_index}).jpg"
        assert result["path"] == expected_path


def test_get_mentioning_day_invalid_day():
    """
    اگر datetime نام روزی خارج از daily_data بازگرداند،
    تابع باید رشته "روز نامشخصی است!" را برگرداند.
    """
    with patch("utils.datetime.datetime") as mock_datetime:
        mock_now = mock_datetime.now.return_value
        mock_now.strftime.return_value = "NotARealDay"

        result = get_mentioning_day()
        assert result == "روز نامشخصی است!"


# ---------- تست تابع sync بدون خطا ----------
def test_safe_run_sync_success():
    @safe_run
    def sample():
        return "ok"

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(sample())
    assert result == "ok"


# ---------- تست تابع sync با خطا ----------
@patch("utils.decorator.error_response")
@patch("utils.decorator.send_to_admins", new_callable=AsyncMock)
def test_safe_run_sync_error(mock_send, mock_error):
    mock_error.return_value = "error_post"

    @safe_run
    def sample():
        raise ValueError("fail")

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(sample())

    assert result == "error_post"
    mock_error.assert_called_once()
    mock_send.assert_awaited_once()


# ---------- تست تابع async بدون خطا ----------
def test_safe_run_async_success():
    @safe_run
    async def sample():
        return "async_ok"

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(sample())
    assert result == "async_ok"


# ---------- تست تابع async با خطا ----------
@patch("utils.decorator.error_response")
@patch("utils.decorator.send_to_admins", new_callable=AsyncMock)
def test_safe_run_async_error(mock_send, mock_error):
    mock_error.return_value = "error_post"

    @safe_run
    async def sample():
        raise RuntimeError("async_fail")

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(sample())

    assert result == "error_post"
    mock_error.assert_called_once()
    mock_send.assert_awaited_once()


# ---------- تست file_id_to_bynery ----------
@pytest.mark.asyncio
async def test_file_id_to_bynery():
    fake_content = b"test bytes"
    mock_bot = MagicMock()
    mock_bot.download = AsyncMock(return_value=fake_content)

    result = await file_id_to_bynery("fake_id", mock_bot)
    assert isinstance(result, io.BytesIO)
    assert result.read() == fake_content


# ---------- تست get_media_bytes برای photo ----------
@pytest.mark.asyncio
async def test_get_media_bytes_photo():
    mock_bot = MagicMock()
    mock_bot.download = AsyncMock(return_value=b"photo_bytes")

    mock_photo = MagicMock()
    mock_photo.id = "photo_id"

    mock_message = MagicMock()
    mock_message.photo = [MagicMock(), mock_photo]
    mock_message.audio = None
    mock_message.video = None

    result = await get_media_bytes(mock_message, mock_bot)
    assert result == (b"photo_bytes", "photo")


# ---------- تست get_media_bytes برای audio ----------
@pytest.mark.asyncio
async def test_get_media_bytes_audio():
    mock_bot = MagicMock()
    mock_bot.download = AsyncMock(return_value=b"audio_bytes")

    mock_audio = MagicMock()
    mock_audio.id = "audio_id"

    mock_message = MagicMock()
    mock_message.photo = None
    mock_message.audio = mock_audio
    mock_message.video = None

    result = await get_media_bytes(mock_message, mock_bot)
    assert result == (b"audio_bytes", "audio")


# ---------- تست get_media_bytes برای video ----------
@pytest.mark.asyncio
async def test_get_media_bytes_video():
    mock_bot = MagicMock()
    mock_bot.download = AsyncMock(return_value=b"video_bytes")

    mock_video = MagicMock()
    mock_video.id = "video_id"

    mock_message = MagicMock()
    mock_message.photo = None
    mock_message.audio = None
    mock_message.video = mock_video

    result = await get_media_bytes(mock_message, mock_bot)
    assert result == (b"video_bytes", "video")


# ---------- تست get_media_bytes بدون فایل ----------
@pytest.mark.asyncio
async def test_get_media_bytes_none():
    mock_bot = MagicMock()
    mock_message = MagicMock()
    mock_message.photo = None
    mock_message.audio = None
    mock_message.video = None

    result = await get_media_bytes(mock_message, mock_bot)
    assert result is False


@pytest.mark.asyncio
async def test_send_to_admins_success_true():
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()
    result = {"message": "hello"}
    await send_to_admins(result, "admin_id", mock_bot, success=True)
    mock_bot.send_message.assert_awaited_once_with("admin_id", "hello")


@pytest.mark.asyncio
async def test_send_to_admins_result_dict_with_success_false():
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()
    result = {"message": "خطا!", "success": False}
    await send_to_admins(result, "admin_id", mock_bot)
    mock_bot.send_message.assert_awaited_once_with("admin_id", "خطا!")


@pytest.mark.asyncio
async def test_send_to_admins_result_dict_with_success_true():
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()
    result = {"message": "همه چیز خوبه", "success": True}
    await send_to_admins(result, "admin_id", mock_bot)
    mock_bot.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_send_to_admins_result_str_success_true():
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock()
    result = "خطای متنی"
    await send_to_admins(result, "admin_id", mock_bot, success=True)
    mock_bot.send_message.assert_awaited_once_with("admin_id", "خطای متنی")


@pytest.mark.asyncio
async def test_send_to_admins_send_message_raises():
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock(side_effect=Exception("ارسال نشد"))
    result = {"message": "خطا!", "success": False}
    # نباید خطا بده
    await send_to_admins(result, "admin_id", mock_bot)
    mock_bot.send_message.assert_awaited_once()


# ---------- تست success_response ----------
def test_success_response_default():
    result = success_response()
    assert result["success"] is True
    assert result["message"] == ""
    assert result["data"] is None


def test_success_response_custom():
    result = success_response("عملیات موفق", {"id": 1})
    assert result["success"] is True
    assert result["message"] == "عملیات موفق"
    assert result["data"] == {"id": 1}


# ---------- تست error_response بدون exception ----------
def test_error_response_without_exception():
    result = error_response("خطا رخ داد")
    assert result["success"] is False
    assert result["message"] == "خطا رخ داد"
    assert result["error_message"] is None
    assert result["error_type"] is None
    assert result["traceback"] is None


# ---------- تست error_response با exception ----------
def test_error_response_with_exception():
    try:
        raise ValueError("مقدار نامعتبر")
    except Exception as e:
        result = error_response("خطا در پردازش", e)
        assert result["success"] is False
        assert result["message"] == "خطا در پردازش"
        assert result["error_message"] == "مقدار نامعتبر"
        assert result["error_type"] == "ValueError"
        assert isinstance(result["traceback"], str)
        assert "ValueError" in result["traceback"]


from utils.schaduler_utils import get_schaduler_state, set_schaduler_state


# ---------- تست get_schaduler_state با مقدار True ----------
def test_get_schaduler_state_true():
    mock_data = json.dumps({"schaduler_state": True})
    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = get_schaduler_state()
        assert result is True


# ---------- تست get_schaduler_state با مقدار False ----------
def test_get_schaduler_state_false():
    mock_data = json.dumps({"schaduler_state": False})
    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = get_schaduler_state()
        assert result is False


# ---------- تست get_schaduler_state بدون کلید ----------
def test_get_schaduler_state_missing_key():
    mock_data = json.dumps({})
    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = get_schaduler_state()
        assert result is False


# ---------- تست set_schaduler_state ----------
def test_set_schaduler_state():
    initial_data = json.dumps({"schaduler_state": False})
    m = mock_open(read_data=initial_data)

    with patch("builtins.open", m):
        set_schaduler_state(True)

    # بررسی اینکه فایل با مقدار جدید نوشته شده
    m.assert_called_with("schaduler_state.json", "w")
    handle = m()
    written = "".join(call.args[0] for call in handle.write.call_args_list)
    assert '"schaduler_state": true' in written.lower()


# ---------- تست split_text_with_index ----------
def test_split_text_with_index_basic():
    text = "سلام به همه دوستان عزیز"
    chunks = split_text_with_index(text, 5)
    assert len(chunks) == 5
    assert chunks[0].startswith("1 از 5\n")
    assert chunks[-1].startswith("5 از 5\n")


def test_split_text_with_index_short_text():
    text = "سلام"
    chunks = split_text_with_index(text, 10)
    assert len(chunks) == 1
    assert chunks[0].startswith("1 از 1\n")
    assert chunks[0].endswith("سلام")


# ---------- تست fa_to_en_int ----------
def test_fa_to_en_int_all_farsi():
    assert fa_to_en_int("۱۲۳۴۵۶۷۸۹۰") == 1234567890


def test_fa_to_en_int_mixed():
    assert fa_to_en_int("۱۲3۴") == 1234


def test_fa_to_en_int_only_english():
    assert fa_to_en_int("2025") == 2025


# ---------- تست prepare_processed_messages ----------
def test_prepare_processed_messages_ordering_and_format():
    parts = [(2, "دوم"), (1, "اول"), (3, "سوم")]
    text_id = "xyz"

    def mock_process(text, tid):
        return f"[{tid}] {text}"

    result = prepare_processed_messages(parts, text_id, mock_process)
    assert len(result) == 3
    assert result[0].startswith("[xyz] 1/3")
    assert "اول" in result[0]
    assert "دوم" in result[1]
    assert "سوم" in result[2]
