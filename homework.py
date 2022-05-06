import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import constants as const
import exceptions as exp

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Эту константу отсюда не убрать. Потому что неправильно
# импортировать что-то из файла с иполняемым кодом.
# А тут надо импортировать PRACTICUM_TOKEN вовне.
# Да и в целом, в прекоде эти константы были тут.
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

# Много места не занимают. Пусть будут тут
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}

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
    except telegram.error.TelegramError as error:
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

    try:
        homework_statuses = requests.get(
            const.ENDPOINT,
            headers=HEADERS,
            params=payload
        )
    except requests.exceptions.RequestException:
        message = f'{const.LOG_MESSAGES["wrong_request"]}'
        raise exp.API_Ya_Practicum_Exception_Endpoint(message)

    answer_code = homework_statuses.status_code
    if answer_code != HTTPStatus.OK:
        message = f'{const.LOG_MESSAGES["wrong_status_code"]}: {answer_code}'
        logger.error(message)
        raise exp.API_Ya_Practicum_Exception_Endpoint(message)

    try:
        return homework_statuses.json()
    except Exception:
        raise ValueError(
            const.LOG_MESSAGES['error_tranform_response_to_diсt']
        )


def check_response(response):
    """
    Выполняет проверку ответа API на соотвествие.
    Возвращает список домашних работ.
    """
    if 'homeworks' not in response:
        message = f'{const.LOG_MESSAGES["missed_key"]} homeworks: {response}'
        raise TypeError(message)

    if not(type(response) is dict):
        message = f'{const.LOG_MESSAGES["wrong_type"]}: {response}'
        raise TypeError(message)

    if not(type(response['homeworks']) is list):
        message = f'{const.LOG_MESSAGES["wrong_type"]}: {response}'
        raise TypeError(message)

    if not response['homeworks']:
        message = f'{const.LOG_MESSAGES["empty_list"]}: {response}'
        logger.debug(message)

    return response['homeworks']


def parse_status(homework):
    """
    Получает информацию о статусе домашней работы.
    Извлекает информацию по ключам homework_name и status из списка
    Возвращает строку с информацией о новом статусе
    """
    if 'homework_name' not in homework:
        message = (
            f'{const.LOG_MESSAGES["missed_key"]} "homework_name": {homework}'
        )
        logger.error(message)
        raise KeyError(message)

    if 'status' not in homework:
        message = (
            f'{const.LOG_MESSAGES["missed_key"]} "status": {homework}'
        )
        logger.error(message)
        raise KeyError(message)

    homework_name = homework['homework_name']
    homework_status = homework['status']

    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError:
        message = (
            f'{const.LOG_MESSAGES["wrong_status"]}: {homework_status}'
        )
        logger.error(message)
        raise ValueError(message)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия переменных окружения."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    # Хочу отдельну проверку на каждый токен
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
            time.sleep(const.RETRY_TIME)

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
            time.sleep(const.RETRY_TIME)

        except (exp.API_Ya_Practicum_Exception_Endpoint,
                ValueError,
                TypeError,
                Exception) as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if last_message != message:
                send_message(bot, message)
                last_message = message

        finally:
            time.sleep(const.RETRY_TIME)


if __name__ == '__main__':
    main()
