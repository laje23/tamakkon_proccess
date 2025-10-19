import os

base_image_url = os.getenv("BASE_IMAGE_URL") or ""
base_mentioning_image_url = os.getenv("BASE_DAY_URL") or ""

hadith_photo_url = base_image_url + "hadith.jpg"
