# utils/media.py
import io


async def file_id_to_bynery(file_id, bot):
    content = await bot.download(file_id)
    bio = io.BytesIO(content)
    bio.seek(0)
    return bio


async def get_media_bytes(message, bot):
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
