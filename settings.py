"""
Константы homework_bot.

HOMEWORK_STATUSES - статусы работ
LOG_MESSAGES - сообщения логирования
"""

LOG_MESSAGES = {
    'app_start': 'homework_bot started ...',
    'app_stop': 'homework_bot stoped: ctrl+c',
    'empty_list': 'Получен пустой список',
    'error_send_message': 'Ошибка отправки сообщения',
    'error_tranform_response_to_diсt':
        'Не удалось преобразовать ответ к словарю',
    'succesfully_send_message': 'Сообщение успешно отправлено',
    'missed_env': 'Отсутствуют переменные окружения',
    'missed_key': 'В ответе отсуствует ключ',
    'wrong_status': 'Статус работы отличается от ожидаемых',
    'wrong_status_code': 'API Yandex практикума вернул код ',
    'wrong_type': 'API вернул ответ некорректного типа',
    'wrong_request': 'API не ответил на запрос',
}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
