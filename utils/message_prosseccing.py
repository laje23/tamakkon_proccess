# utils/message_processing.py

def process_hadith_message(text: str, id: int | str, eitaa=False) -> str:
    if eitaa:
        return f"""📗 حدیث روز 
{text}\n
#حدیث
#{id}
@tamakkon_ir"""
    return f"""📗 حدیث روز
{text}\n
#حدیث
#{id}
@tamakkon_ir"""


def process_note_message(text: str, id: int | str) -> str:
    emoji_map = {i: num for i, num in enumerate(["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"])}
    emojied = "".join(emoji_map[int(c)] for c in str(id)[::-1])
    return f"""#یادداشت_استاد
شماره {emojied}

{text}

صفحه رسمی استاد در فارس من:
https://farsnews.ir/shnavvab

#نهضت_تمکن
@tamakkon_ir"""
