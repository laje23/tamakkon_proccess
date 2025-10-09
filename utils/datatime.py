# utils/datetime_utils.py
import jdatetime
from datetime import datetime
from config import base_mentioning_image_url


def get_mentioning_day():
    daily_data = {
        "Saturday": {
            "fa": "شنبه",
            "zekr": "یا رب العالمین",
            "image_path": f"{base_mentioning_image_url} (1).jpg",
        },
        "Sunday": {
            "fa": "یک‌شنبه",
            "zekr": "یا ذاالجلال و الاکرام",
            "image_path": f"{base_mentioning_image_url} (2).jpg",
        },
        "Monday": {
            "fa": "دوشنبه",
            "zekr": "یا قاضی الحاجات",
            "image_path": f"{base_mentioning_image_url} (3).jpg",
        },
        "Tuesday": {
            "fa": "سه‌شنبه",
            "zekr": "یا ارحم الراحمین",
            "image_path": f"{base_mentioning_image_url} (4).jpg",
        },
        "Wednesday": {
            "fa": "چهارشنبه",
            "zekr": "یا حی یا قیوم",
            "image_path": f"{base_mentioning_image_url} (5).jpg",
        },
        "Thursday": {
            "fa": "پنج‌شنبه",
            "zekr": "لا اله الا الله الملک الحق المبین",
            "image_path": f"{base_mentioning_image_url} (6).jpg",
        },
        "Friday": {
            "fa": "جمعه",
            "zekr": "اللهم صل علی محمد و آل محمد",
            "image_path": f"{base_mentioning_image_url} (7).jpg",
        },
    }

    today = datetime.now()
    day_en = today.strftime("%A")
    info = daily_data.get(day_en)
    if not info:
        return "روز نامشخصی است!"

    today_jalali = jdatetime.datetime.now()
    date_str = today_jalali.strftime("%Y/%m/%d")

    return {
        "name": info["fa"],
        "zekr": info["zekr"],
        "date": date_str,
        "path": info["image_path"],
    }
