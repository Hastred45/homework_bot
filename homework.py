import logging
import os
import time

from http import HTTPStatus

import requests
import telegram

from dotenv import load_dotenv
import sys

import constants as const
import exceptions as exp

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщений в телеграмм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(
            f'{const.LOG_MESSAGES["succesfully_send_message"]}: {message}'
        )
    except Exception as error:
        raise exp.Telegram_Exception(
            f'{const.LOG_MESSAGES["error_send_message"]}: {error}'
        )


def get_api_answer(current_timestamp):
    """
    Выполняет запрос к API на получение новых статусов ДР.
    Полученный json-массив преобразуется в словарь
    """
    timestamp = current_timestamp or int(time.time())
    payload = {'from_date': timestamp}
    homework_statuses = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=payload
    )
    answer_code = homework_statuses.status_code
    if answer_code != HTTPStatus.OK:
        message = f'{const.LOG_MESSAGES["wrong_status_code"]}: {answer_code}'
        logger.error(message)
        raise exp.API_Ya_Practicum_Exception_Endpoint(message)

    try:
        return dict(homework_statuses.json())
    except Exception:
        raise ValueError(
            const.LOG_MESSAGES['error_tranform_response_to_diсt']
        )


def check_response(response):
    """
    Выполняет проверку ответа API на соотвествие.
    Возвращает список домашних работ.
    """
    if (not(type(response) is dict)
       or not(type(response['homeworks']) is list)):
        message = f'{const.LOG_MESSAGES["wrong_type"]}: {response}'
        raise TypeError(message)

    if 'homeworks' not in response:
        message = f'{const.LOG_MESSAGES["missed_key"]} homeworks: {response}'
        raise TypeError(message)

    if len(response['homeworks']) < 1:
        message = f'{const.LOG_MESSAGES["empty_list"]}: {response}'
        logger.debug(message)

    return response['homeworks']


def parse_status(homework):
    """
    Получает информацию о статусе домашней работы.
    Извлекает информацию по ключам homework_name и status из списка
    Возвращает строку с информацией о новом статусе
    """
    for key in const.HOMEWORK_KEYS:
        if key not in homework:
            message = (
                f'{const.LOG_MESSAGES["missed_key"]} {key}: {homework}'
            )
            logger.error(message)
            raise KeyError(message)

    if homework['status'] not in const.HOMEWORK_STATUSES.keys():
        message = (
            f'{const.LOG_MESSAGES["wrong_status"]}: {homework["status"]}'
        )
        logger.error(message)
        raise ValueError(message)

    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = const.HOMEWORK_STATUSES[homework_status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия переменных окружения."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    result = True
    for token, value in tokens.items():
        if value is None:
            result = False
            logger.critical(f'{const.LOG_MESSAGES["missed_env"]}: {token}')

    return result


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = const.LOG_MESSAGES['missed_env']
        raise EnvironmentError(message)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    message = const.LOG_MESSAGES['app_start']
    logger.info(message)
    send_message(bot, message)

    last_message = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            for homework in check_response(response):
                message = parse_status(homework)
                send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except EnvironmentError as error:
            logger.info(error)
            return

        except KeyboardInterrupt:
            message = const.LOG_MESSAGES['app_stop']
            logger.info(message)
            send_message(bot, message)
            return

        except exp.Telegram_Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            time.sleep(RETRY_TIME)

        except (exp.API_Ya_Practicum_Exception_Endpoint,
                ValueError,
                TypeError,
                Exception) as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if last_message != message:
                send_message(bot, message)
                last_message = message
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
