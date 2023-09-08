import time
import traceback
import sys
from typing import Union
import logging
from time import sleep

import config
import chatGPT
import db_class
import telegram_class


class Bot_logic():
    _db: db_class.DB
    _telegram: telegram_class.Bot
    _logger: logging

    def __init__(self) -> None:
        self._db = db_class.DB(config.DB_USER, config.DB_PASSWORD, config.DB_NAME)
        self._telegram = telegram_class.Bot(config.TOKEN)
        self._chatBot = chatGPT.ChatGPT(update_extension=False)
        logging.basicConfig(filename='main.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self._logger = logging.getLogger(__name__)
        try:
            self._logger.info("start selenium")
            self._chatBot.authorization()
        except Exception as ex:
            self._logger.error(f"Exception: {ex} {traceback.print_exc()}")
            self._chatBot.finish_work()
            sys.exit(0)

    def _get_user_status(self, chat_id: int, user_name: str) -> bool:
        if user := self._db.get_user(chat_id):
            return bool(user[2])
        else:
            self._db.create_user(chat_id, user_name)
            return bool(self._db.get_user(chat_id)[2])

    def _get_message_status(self, chat_id: int, message: str, message_id: int) -> Union[int, None]:
        if (result := self._db.get_message(chat_id, message_id)) is not None:
            return result
        else:
            self._db.create_message(chat_id, message, message_id)
            return self._db.get_message(chat_id, message_id)

    def _get_all_users_list(self) -> str:
        return '\r\n'.join([f"{temp[1]} ({temp[0]})" for temp in self._db.get_all_users()])

    def _send_answer(self, answer: str, chat_id: int, reply: int = 0) -> bool:
        result = self._telegram.send_message(chat_id, answer, reply)
        if result["success"]:
            self._db.update_message(chat_id, answer, reply, result["data"]["result"]["message_id"])
            return True
        else:
            self._logger.error(f"_send_answer {result['data']}")
            self._logger.error(f"_send_answer {result['errors']}")
            return False

    def _prepare_help_message(self) -> str:
        return config.BOT_STATIC_ANSWER_INFO

    def _ban_user_by_chat_id(self, chat_id: int) -> str:
        self._db.ban_user_by_chat_id(chat_id)
        return config.BOT_STATIC_ANSWER_BAN.format(chat_id=chat_id)

    def working(self, sleep_time: int = 5) -> None:
        stop_word: bool = True
        while stop_word:
            self._logger.info(f"main loop  new iteration")
            messages = self._telegram.get_messages()
            if messages["success"]:
                for message in messages["data"]:
                    if self._get_user_status(message[0], message[2]):
                        res_of_get_message_status = self._get_message_status(message[0], message[1], message[3])
                        self._logger.info(f"working with   {message} {res_of_get_message_status}")
                        if res_of_get_message_status is None:
                            self._logger.info(f"DB error   {message}")
                        elif res_of_get_message_status == 0:
                            text_of_message = message[1].lower()
                            if text_of_message == config.COMMAND_SHOW_ALL_USERS:
                                result = self._send_answer(self._get_all_users_list(), message[0], message[3])
                                self._logger.info(f"COMMAND_SHOW_ALL_USERS result of work {result}")
                            elif text_of_message == config.COMMAND_HELP:
                                result = self._send_answer(self._prepare_help_message(), message[0], message[3])
                                self._logger.info(f"COMMAND_HELP result of work {result}")
                            elif text_of_message == config.COMMAND_CLEAR_HISTORY:
                                result = self._send_answer("don't work", message[0], message[3])
                                self._logger.info(f"COMMAND_CLEAR_HISTORY result of work {result}")
                            elif text_of_message == config.COMMAND_ADD_NEW_USER:
                                result = self._send_answer("done", message[0], message[3])
                                self._logger.info(f"COMMAND_ADD_NEW_USER result of work {result}")
                            elif text_of_message == config.COMMAND_RESTART_SELENIUM:
                                self._send_answer("restarting...", message[0], message[3])
                                restart_status: bool = False
                                try:
                                    self._logger.info("restart selenium")
                                    self._chatBot.finish_work()
                                    time.sleep(5)
                                    self._chatBot = chatGPT.ChatGPT(update_extension=False)
                                    restart_status = self._chatBot.authorization()
                                except Exception as ex:
                                    self._logger.error(f"Exception: {ex} {traceback.print_exc()}")
                                if restart_status:
                                    self._send_answer("restart success", message[0], message[3])
                                else:
                                    self._send_answer("restart fault", message[0], message[3])
                            elif text_of_message == config.COMMAND_STOP_WORD:
                                result = self._send_answer("bye", message[0], message[3])
                                self._logger.info(f"COMMAND_STOP_WORD result of work {result}")
                                self._chatBot.finish_work()
                                stop_word = False
                            elif set(config.COMMAND_BAN_USER_BY_CHAT_ID.split()) < set(text_of_message.split()):
                                result = self._send_answer(self._ban_user_by_chat_id(
                                    int((set(text_of_message.split()) - set(
                                        config.COMMAND_BAN_USER_BY_CHAT_ID.split())).pop())),
                                    message[0], message[3])
                                self._logger.info(f"COMMAND_BAN_USER_BY_CHAT_ID result of work {result}")
                            else:
                                self._logger.info(f"request to chat bot")
                                self._send_answer("Готовим ответ", message[0], message[3])
                                try:
                                    self._send_answer(self._chatBot.ask_bot(message[1]), message[0], message[3])
                                    self._logger.info(f"success")
                                except Exception as ex:
                                    self._logger.error(f"Exception: {ex} {traceback.print_exc()}")
                                    self._chatBot.finish_work()
                                    self._send_answer(config.BOT_STATIC_ANSWER_ERROR, message[0], message[3])
                        else:
                            self._logger.info(f"done with   {message} ")

                    else:
                        self._logger.info(f"{message[2]} ({message[0]}) {message[1]}  access denied")
            else:
                self._logger.error(f"have been unable to get messages {messages['data']}")
                self._logger.error(f" {messages['errors']}")
                stop_word = False
            sleep(sleep_time)
        self._logger.info(f"stop working")


if __name__ == '__main__':
    main = Bot_logic()
    main.working()
