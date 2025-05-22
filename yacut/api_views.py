import re

from flask import jsonify, request, url_for

from . import app, db
from .models import URLMap
from .utils import generate_short_url
from .error_handlers import InvalidAPIUsage
from .constants import SHORT_ID_MAX_LENGTH, SHORT_ID_REGEX


@app.route('/api/id/', methods=['POST'])
def create_url():
    _validate_request()
    data = _get_json_data()
    original_url, custom_id = _extract_url_data(data)
    short_id = (
        _process_custom_id(custom_id)
        if custom_id
        else generate_short_url()
    )
    url_map = URLMap(original=original_url, short=short_id)
    db.session.add(url_map)
    db.session.commit()
    return jsonify({
        'url': original_url,
        'short_link': url_for(
            'redirect_to_original', short_id=short_id, _external=True
        )
    }), 201


def _validate_request():
    if request.content_type != 'application/json':
        raise InvalidAPIUsage(
            'Неверный Content-Type: ожидается application/json'
        )


def _get_json_data():
    if not request.data:
        raise InvalidAPIUsage('Отсутствует тело запроса', 400)
    try:
        data = request.get_json()
    except Exception:
        raise InvalidAPIUsage('Неверный формат JSON', 400)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса', 400)
    return data


def _extract_url_data(data):
    original_url = data.get('url')
    if not original_url:
        raise InvalidAPIUsage(
            '"url" является обязательным полем!'
        )
    return original_url, data.get('custom_id')


def _process_custom_id(custom_id):
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


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), 200
