import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from logging import StreamHandler, Formatter

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update

from gpt.ygpt import get_gpt_reply

log = logging.getLogger('__name__')
file_handler = RotatingFileHandler("main.log", maxBytes=500_000, backupCount=5)
stream_handler = StreamHandler(sys.stdout)
formatter = Formatter('%(asctime)s [%(levelname)s] %(funcName)s %(lineno)d %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
log.addHandler(file_handler)
log.addHandler(stream_handler)
log.setLevel(logging.DEBUG)

load_dotenv()

TELEGRAM_TOKEN=os.getenv('TELEGRAM_TOKEN')
ADMIN_TELEGRAM_CHAT_ID=int(os.getenv('ADMIN_TELEGRAM_CHAT_ID'))

AUTH_USERS={0, ADMIN_TELEGRAM_CHAT_ID}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greating users preliminary validated."""
    chat_id = update.effective_user.id
    log.debug(f"Начало работы бота для пользователя {chat_id}")
    if chat_id in AUTH_USERS:
        await update.get_bot().send_message(chat_id, 'Добро пожаловать!')
    else:
        log.debug(f'Пользователь с {chat_id=} пытался использовать бота')
        await update.get_bot().send_message(chat_id, 'бот еще в разработке')


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    text = update.message.text
    log.debug(f"Начало обработки текста {text} пользователя {chat_id} ")
    reply = await get_gpt_reply(text)
    log.debug(f"Отправка ответа {reply} пользователю {chat_id} ")
    await update.get_bot().send_message(chat_id, reply)

if __name__ == '__main__':
    assert TELEGRAM_TOKEN is not None

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # validating user by its id (currently supporting only 2 users)
    app.add_handler(CommandHandler('start', start))

    app.add_handler(MessageHandler(filters.TEXT, process_message))

    app.run_polling(1.0, allowed_updates=Update.ALL_TYPES)

    # getting text request from user id

    # validating user has not exceeded used tokens per day

    # sending user info about waiting for reply (Processing your request...)
    # sending the text request to async gpt model and getting operation id
    # polling operation api to get response

    # from response saving info about used tokens for specific user
    # checking used tokens per day for user
    # sending response text to user
    # if tokens threshold per day exceeded than send info to user about it