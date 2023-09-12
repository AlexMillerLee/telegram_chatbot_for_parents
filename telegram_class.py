import traceback

import requests
import json


class Bot:
    _token: str = ""

    def __init__(self, token) -> None:
        self._token = token

    def get_messages(self, limit: int = 100, offset: int = 0, timeout: int = 0) -> dict:
        """

        :param limit:
        :param offset:
        :param timeout:
        :return:  {success: true/false; data: messages (chat_id , message, username)  ;  errors : list of error  }
        """

        url = f"https://api.telegram.org/bot{self._token}/getUpdates"
        headers = {
            "Content-Type": "application/json",
        }
        data = {"limit": 100}
        if 100 > limit > 0:
            data["limit"] = limit
        if offset != 0:
            data["offset"] = offset
        if timeout != 0:
            data["timeout"] = timeout
        result = dict()
        try:
            response = requests.post(url, headers=headers, params=data)
        except Exception as ex:
            result["data"] = None
            result["success"] = False
            result["errors"] = [f"{ex}", f"{traceback.print_exc()}"]
            return result
        answer = response.json()
        if response.status_code == 200:
            if answer["ok"]:
                result["data"] = self._prepare_message_dict(answer["result"])
                result["success"] = True
                result["errors"] = []
            else:
                result["data"] = answer
                result["success"] = True
                result["errors"] = ["неизвестная ошибка смотри data"]
        else:
            result["data"] = None
            result["success"] = False
            result["errors"] = [f"Ошибка статуса ответа {response.status_code}"]
        return result

    def _prepare_message_dict(self, raw: list) -> list:
        """
        :param raw: dict from telegram API
        :return: (chat_id , message, username, message_id)
        """
        return [(temp["message"]["chat"]["id"], temp["message"]["text"], temp["message"]["chat"]["username"],
                 temp["message"]["message_id"]) for temp
                in raw]

    def send_message(self, chat_id: int, message: str, reply: int = 0) -> dict:
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "text": message,
            "chat_id": chat_id
        }
        if reply != 0:
            data["reply_to_message_id"] = reply
        response = requests.post(url, headers=headers, data=json.dumps(data, ensure_ascii=True))
        result = {}
        answer = response.json()
        if answer["ok"]:
            result["data"] = answer
            result["success"] = True
            result["errors"] = []
        else:
            result["data"] = None
            result["success"] = False
            result["errors"] = answer["errors"]
        return result
