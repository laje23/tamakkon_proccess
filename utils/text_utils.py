# utils/text_utils.py
from config import process_note_message


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
    return int(result)


def prepare_processed_messages(parts, text_id):
    parts_sorted = sorted(parts, key=lambda x: x[0])
    total = len(parts_sorted)
    messages = []
    for i, (_, content) in enumerate(parts_sorted, start=1):
        numbered_text = f"{i}/{total} \n {content}"
        processed = process_note_message(numbered_text, text_id)
        messages.append(processed)
    return messages
