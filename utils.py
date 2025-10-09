import json
import traceback
from datetime import datetime
import jdatetime
import io
from config import base_mentioning_image_url, process_note_message


async def get_media_bytes(message, bot) -> bytes | None:
    file_id = None
    type_file = None
    if message.photo:
        photo = message.photo[-1]
        file_id = photo.id
        type_file = "photo"
    elif message.audio:
        file_id = message.audio.id
        type_file = "audio"
    elif message.video:
        file_id = message.video.id
        type_file = "video"

    if file_id is None:
        return False

    bio = await file_id_to_bynery(file_id, bot)
    bin_file = bio.read()
    return bin_file, type_file


async def file_id_to_bynery(file_id, bot):
    content = await bot.download(file_id)
    bio = io.BytesIO(content)
    bio.seek(0)
    return bio


def get_mentioning_day():
    daily_data = {
        "Saturday": {
            "fa": "شنبه",
            "zekr": "یا رب العالمین",
            "image_path": f"{base_mentioning_image_url} (1).jpg",
            "text": "امروز شنبه است، روزی برای شروع تازه.",
        },
        "Sunday": {
            "fa": "یک‌شنبه",
            "zekr": "یا ذاالجلال و الاکرام",
            "image_path": f"{base_mentioning_image_url} (2).jpg",
            "text": "یک‌شنبه، روزی پر از انرژی و امید.",
        },
        "Monday": {
            "fa": "دوشنبه",
            "zekr": "یا قاضی الحاجات",
            "image_path": f"{base_mentioning_image_url} (3).jpg",
            "text": "دوشنبه، فرصتی دوباره برای تلاش.",
        },
        "Tuesday": {
            "fa": "سه‌شنبه",
            "zekr": "یا ارحم الراحمین",
            "image_path": f"{base_mentioning_image_url} (4).jpg",
            "text": "سه‌شنبه، روز بخشش و مهربانی.",
        },
        "Wednesday": {
            "fa": "چهارشنبه",
            "zekr": "یا حی یا قیوم",
            "image_path": f"{base_mentioning_image_url} (5).jpg",
            "text": "چهارشنبه، روزی برای تامل و اندیشه.",
        },
        "Thursday": {
            "fa": "پنج‌شنبه",
            "zekr": "لا اله الا الله الملک الحق المبین",
            "image_path": f"{base_mentioning_image_url} (6).jpg",
            "text": "پنج‌شنبه، روز تلاش و موفقیت.",
        },
        "Friday": {
            "fa": "جمعه",
            "zekr": "اللهم صل علی محمد و آل محمد",
            "image_path": f"{base_mentioning_image_url} (7).jpg",
            "text": "جمعه، روز آرامش و استراحت.",
        },
    }
    today = datetime.now()
    day_en = today.strftime("%A")
    info = daily_data.get(day_en)

    if not info:
        return "روز نامشخصی است!"

    day_fa = info["fa"]
    zekr = info["zekr"]
    url = info["image_path"]

    today_jalali = jdatetime.datetime.now()
    date_str = today_jalali.strftime("%Y/%m/%d")

    return {
        "name": day_fa,
        "zekr": zekr,
        "date": date_str,
        "path": url,
    }


# utils/response.py


def success_response(message="", data=None):
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str, exception: Exception = None):
    return {
        "success": False,
        "message": message,
        "error_type": type(exception).__name__ if exception else None,
        "traceback": traceback.format_exc() if exception else None,
    }


STATE_FILE = "schaduler_state.json"


def get_schaduler_state():
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
    return data.get("schaduler_state", False)


def set_schaduler_state(value: bool):
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
    data["schaduler_state"] = value
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def split_text_with_index(text, chunk_size):
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    total = len(chunks)
    formatted_chunks = []
    for i, chunk in enumerate(chunks, 1):
        header = f"{i} از {total}\n"
        formatted_chunks.append(header + chunk)
    return formatted_chunks


def fa_to_en_int(num):
    fa_digits = "۰۱۲۳۴۵۶۷۸۹"
    en_digits = "0123456789"
    result = ""
    for ch in str(num):
        if ch in fa_digits:
            result += en_digits[fa_digits.index(ch)]
        elif ch in en_digits:
            result += ch
        else:
            continue
    return int(result)


def prepare_processed_messages(parts, text_id):
    # مرتب کردن بخش‌ها بر اساس part_index
    parts_sorted = sorted(parts, key=lambda x: x[0])

    total = len(parts_sorted)
    messages = []

    for i, (_, content) in enumerate(parts_sorted, start=1):
        # اضافه کردن شماره بخش
        numbered_text = f"{i}/{total} \n {content}"

        # پردازش متن
        processed = process_note_message(numbered_text, text_id)

        # ذخیره در لیست
        messages.append(processed)

    return messages
