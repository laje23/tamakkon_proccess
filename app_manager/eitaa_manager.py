import mimetypes
import httpx


class EitaaBot:

    def __init__(self, eitaa_bot_token):
        self.bot_token_eitaa = eitaa_bot_token
        self.eitaa_base_url = f"https://eitaayar.ir/api/{eitaa_bot_token}"

    async def send_message(self, chat_id: int, text: str):
        url = f"{self.eitaa_base_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            res = await client.post(url, json=payload)
            dic = res.json()
            if dic["ok"] == "true":
                return True
            return False

    async def send_file(self, chat_id: int, file, caption=""):
        url = f"{self.eitaa_base_url}/sendFile"
        payload = {
            "chat_id": chat_id,
            "caption": caption,
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            if isinstance(file, str):
                mime_type, _ = mimetypes.guess_type(file)
                with open(file, "rb") as f:
                    files = {"file": (file, f, mime_type or "application/octet-stream")}
                    res = await client.post(url, data=payload, files=files)
            else:
                files = {"file": ("video.mp4", file, "video/mp4")}
                res = await client.post(url, data=payload, files=files)

        dic = res.json()
        return dic.get("ok") == "true"
