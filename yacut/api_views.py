from flask import jsonify, url_for

from . import app, db
from .models import URLMap
from .utils import (
    generate_short_url, validate_request, get_json_data,
    extract_url_data, process_custom_id
)
from .error_handlers import InvalidAPIUsage
from .constants import STATUS_OK, NOT_FOUND, CREATED


@app.route('/api/id/', methods=['POST'])
def create_url():
    validate_request()
    data = get_json_data()
    original_url, custom_id = extract_url_data(data)
    short_id = (
        process_custom_id(custom_id)
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
    }), CREATED


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        raise InvalidAPIUsage('Указанный id не найден', NOT_FOUND)
    return jsonify({'url': url_map.original}), STATUS_OK
