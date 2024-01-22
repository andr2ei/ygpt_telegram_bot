import os
import asyncio
from http import HTTPStatus
import sys
import logging
from logging import StreamHandler, Formatter
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from requests import post, get

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

YANDEX_GPT_SERVICE_API_KEY=os.getenv('YANDEX_GPT_SERVICE_API_KEY')
YANDEX_FOLDER=os.getenv('YANDEX_FOLDER')

MAX_ATTEMPTS_TO_GET_RESULT = 20

async def get_gpt_reply(message: str) -> str:
    assert YANDEX_GPT_SERVICE_API_KEY is not None

    headers = {'Authorization': f'Api-Key {YANDEX_GPT_SERVICE_API_KEY}',
               'Content-Type': 'application/json'}

    body = {
        "modelUri": f"gpt://{YANDEX_FOLDER}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.1,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "user",
                "text": message
            }
        ]
    }

    log.debug('Запрос completionAsync foundationModels v1')
    resp_async = post("https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync",
                      headers=headers, json=body)

    assert resp_async.status_code == HTTPStatus.OK
    log.debug('Запрос completionAsync foundationModels v1 вернул 200')

    operation_id = resp_async.json()['id']
    log.debug(f'Запрос completionAsync foundationModels v1 вернул {operation_id=}')

    counter = 0
    while True:
        counter += 1
        await asyncio.sleep(1)
        log.debug(f'Запрос к {operation_id=}')
        resp_async = get(f"https://llm.api.cloud.yandex.net/operations/{operation_id}",
                         headers=headers)
        assert resp_async.status_code == HTTPStatus.OK
        log.debug(f'Запрос к {operation_id=} вернул 200')

        resp_async_j = resp_async.json()

        if resp_async_j['done']:
            return resp_async_j['response']['alternatives'][0]['message']['text']

        if counter > MAX_ATTEMPTS_TO_GET_RESULT:
            return 'сервис временно недоступен, попробуйте позже'