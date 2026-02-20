# utils/datetime_utils.py
import jdatetime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from config.urls import base_mentioning_image_url


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


from zoneinfo import ZoneInfo
from babel.dates import format_date


def get_days_until_friday_fa(tz="Asia/Tehran"):
    today = datetime.now(ZoneInfo(tz)).date()
    result = []

    for i in range(7):
        d = today + timedelta(days=i)
        jalali_date = jdatetime.date.fromgregorian(date=d)

        result.append(
            {
                "date_gregorian": d.isoformat(),
                "date_jalali": jalali_date.strftime("%Y/%m/%d"),
                "day": format_date(d, "EEEE", locale="fa"),
            }
        )

    return result


from datetime import datetime
import pytz
import jdatetime


def combine_date_and_time_auto(date_str: str, time_str: str) -> datetime:
    """
    date_str: 'YYYY-MM-DD' (میلادی) یا 'YYYY/MM/DD' (شمسی)
    time_str: 'H' | 'H:M' | 'H:M:S'

    خروجی:
    - تاریخ شمسی → tzinfo = Asia/Tehran
    - تاریخ میلادی → tzinfo = UTC
    """

    # بخش‌های ساعت
    parts = time_str.split(":")
    parts += ["00"] * (3 - len(parts))  # اگر ثانیه یا دقیقه وارد نشده باشه صفر می‌گیره
    h, m, s = [int(p) for p in parts]

    if "/" in date_str:  # تاریخ شمسی
        jy, jm, jd = map(int, date_str.split("/"))
        g_date = jdatetime.date(jy, jm, jd).togregorian()
        dt_naive = datetime(g_date.year, g_date.month, g_date.day, h, m, s)
        iran_tz = pytz.timezone("Asia/Tehran")
        dt = iran_tz.localize(dt_naive)

    else:  # تاریخ میلادی
        y, mo, d = map(int, date_str.split("-"))
        dt_naive = datetime(y, mo, d, h, m, s)
        dt = dt_naive.replace(tzinfo=pytz.UTC)

    return dt


def gregorian_to_jalali(date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    dt = datetime.strptime(date_str, fmt)
    jdt = jdatetime.datetime.fromgregorian(datetime=dt)
    return jdt.strftime("%Y/%m/%d %H:%M:%S")