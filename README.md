# telegram_chatbot_for_parents
Очередной «chatGPT» для телеги,  ничего нового. Просто было скучно, и хотел познакомить родителей с этой вундервафлей. Вариант  c веб версией - сложно,  Россия железный занавес и т.п. Работает в связке с selenium  и mysql, платить за API  не хочется. Mysql  для хранения данных
База данных:
` messages `  Сообщения,  чтобы не отвечать на них повторно
` users `  Пользователи, чтобы банить их. Проект запущен на ноуте из 2005,  так что  на массовое использование бот не рассчитан
Что требуется :
requirements.txt - Это нужно  установить для работы 
db.sql -  Импортировать  в базу данных
default_config.py – Файл конфигураций, нужно заполнить и переименовать  в   config.py
файл config.py: 
TOKEN = ""  - Токен телеграм бота
DB_USER = "" 
DB_PASSWORD = ""
DB_NAME = "" Это все для доступа к MySQL

COMMAND_SHOW_ALL_USERS = " show users "  Команда выводит список пользователей вам в телегу пример: show users
COMMAND_BAN_USER_BY_CHAT_ID = " ban user "  Команда позволяет забанить пользователя пример: ban user -  полная  команда будет ban user 123456 , где 123456 его CHAT_ID (посмотреть можно командой выше) 
COMMAND_HELP = "/help" Dыводит справку 
COMMAND_CLEAR_HISTORY = "/clear_history" - Yе работает пока
COMMAND_ADD_NEW_USER = "/start" -  Просто добавит пользователя в БД 
COMMAND_STOP_WORD = "Хочу на ручки" -  Останавливает программу 

CHAT_GPT_USERNAME = ""  Логин 
CHAT_GPT_PASSWORD = ""  и пароль к аккаунту chatGPT
PATH_TO_DRIVER = ""  Путь к драйверу

PROXY_IP = ""
PROXY_PORT = ""
PROXY_PORT_SOCKET = ""
PROXY_USER = ""
PROXY_PASS = ""  Ваше прокси. Если прокси не нужно, то запускайте с параметром use_proxy: False   пример self._chatBot = chatGPT.ChatGPT(update_extension=False, use_proxy=False) (main.py)


BOT_STATIC_ANSWER_BAN = "Пользователь {chat_id} забанен, если такой был"
BOT_STATIC_ANSWER_ERROR = "Something wrong ((("
BOT_STATIC_ANSWER_INFO = "Тут информация о боте"    - Константы ответов на статические сообщения 

Константы для работы с селениум: (трогать не нужно) 
CHAT_GPT_AUTH_FIRST_BTN = 'button[data-testid = "login-button"]'
CHAT_GPT_AUTH_USER_FIELD = 'input[name="username"]'
CHAT_GPT_AUTH_USER_BTN = 'button[data-action-button-primary="true"]'
CHAT_GPT_AUTH_PASSWORD_FIELD = 'input[name="password"]'
CHAT_GPT_QUESTION_FIELD = 'textarea[id = "prompt-textarea"]'
CHAT_GPT_INF_BTN = 'div[class="flex flex-row justify-end"]'
CHAT_GPT_INF_WAIT_LOAD_CHAT = 'h2[id="radix-:rg:"]'
CHAT_GPT_PROCESSING = 'div[class="text-2xl"]'
CHAT_GPT_ANSWER = 'div[class="markdown prose w-full break-words dark:prose-invert light"]'  

ПС: Сомневаюсь, что вообще хоть кто-то будет это читать.
ПСС:  Пейте пиво, творите добро)  
