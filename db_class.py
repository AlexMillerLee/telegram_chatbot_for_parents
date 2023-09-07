import pymysql
from datetime import datetime
from typing import Union


class DB:
    _user: str = ""
    _password: str = ""
    _db_name: str = ""
    _connect = None
    _cur = None

    def __init__(self, user: str, password: str, db_name: str) -> None:
        self._user = user
        self._password = password
        self._db_name = db_name

    def _connectToDb(self) -> None:
        self._connect = pymysql.connect(
            host='localhost',
            port=3306,
            user=self._user,
            password=self._password,
            database=self._db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        self._cur = self._connect.cursor()

    def _closeconnectionToDb(self):
        self._cur.close()
        self._connect.close()

    def get_user(self, chat_id: int) -> tuple:
        self._connectToDb()
        self._cur.execute(f"SELECT * FROM `users` WHERE `chat_id` = {chat_id} ;")
        rows = self._cur.fetchall()
        self._closeconnectionToDb()
        if len(rows):
            return (rows[0]["chat_id"], rows[0]['user_name'], rows[0]['is_allowed'])
        return tuple()

    def create_user(self, chat_id: int, user_name: str) -> None:
        self._connectToDb()
        self._cur.execute(
            f"INSERT INTO `users`( `chat_id`, `user_name`) VALUES ('{chat_id}','{user_name}');")
        self._connect.commit()
        self._closeconnectionToDb()

    def get_message(self, chat_id: int, message_id: int) -> Union[int, None]:
        self._connectToDb()
        self._cur.execute(f"SELECT * FROM `messages` WHERE `chat_id` = {chat_id} AND `message_id` = {message_id}")
        rows = self._cur.fetchall()
        self._closeconnectionToDb()
        if len(rows):
            return int(rows[0]["is_answered"])
        return None

    def create_message(self, chat_id: int, message: str, message_id: int) -> None:
        self._connectToDb()
        self._cur.execute(
            f"INSERT INTO `messages`( `chat_id`, `message`, `message_id`,`date_get`) VALUES ('{chat_id}','{message}','{message_id}','{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');")
        self._connect.commit()
        self._closeconnectionToDb()

    def get_all_users(self) -> tuple:
        self._connectToDb()
        self._cur.execute(f"SELECT `chat_id`,`user_name` FROM `users`;")
        rows = self._cur.fetchall()
        self._closeconnectionToDb()
        result = list()
        for row in rows:
            result.append((row["chat_id"], row["user_name"]))
        return tuple(result)

    def update_message(self, chat_id: int, answer: str, reply: int, message_id: int) -> None:
        self._connectToDb()
        self._cur.execute(
            f"UPDATE `messages` SET `is_answered`='1',`answer`='{answer}',`date_answer`='{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}',`answer_id`='{message_id}' WHERE `chat_id` = {chat_id} AND `message_id`= {reply};")
        self._connect.commit()
        self._closeconnectionToDb()

    def ban_user_by_chat_id(self, chat_id: int) -> None:
        self._connectToDb()
        self._cur.execute(
            f"UPDATE `users` SET `is_allowed`='0' WHERE `chat_id` = {chat_id};")
        self._connect.commit()
        self._closeconnectionToDb()
