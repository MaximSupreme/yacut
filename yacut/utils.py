import random
import string
import re

from flask import request

from .models import URLMap
from .constants import SHORT_ID_MAX_LENGTH, SHORT_ID_REGEX, BAD_REQUEST
from .error_handlers import InvalidAPIUsage


def generate_short_url(length=6):
    letters = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choice(letters) for _ in range(length))
        if not URLMap.query.filter_by(short=short_id).first():
            return ''.join(random.choice(letters) for _ in range(length))


def validate_request():
    if request.content_type != 'application/json':
        raise InvalidAPIUsage(
            'Неверный Content-Type: ожидается application/json'
        )


def get_json_data():
    if not request.data:
        raise InvalidAPIUsage('Отсутствует тело запроса', BAD_REQUEST)
    try:
        data = request.get_json()
    except Exception:
        raise InvalidAPIUsage('Неверный формат JSON', BAD_REQUEST)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса', BAD_REQUEST)
    return data


def extract_url_data(data):
    original_url = data.get('url')
    if not original_url:
        raise InvalidAPIUsage(
            '"url" является обязательным полем!'
        )
    return original_url, data.get('custom_id')


def process_custom_id(custom_id):
    if len(custom_id) > SHORT_ID_MAX_LENGTH:
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки'
        )
    if not re.match(SHORT_ID_REGEX, custom_id):
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки'
        )
    if URLMap.query.filter_by(short=custom_id).first():
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.'
        )
    return custom_id
