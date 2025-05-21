from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, URL, Optional, Regexp

from .constants import SHORT_ID_MAX_LENGTH, SHORT_ID_REGEX


class URLForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле!'),
            URL(message='Некорректный URL!'),
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(max=SHORT_ID_MAX_LENGTH),
            Regexp(
                SHORT_ID_REGEX,
                message=(
                    'Можно использовать только буквы, цифры и подчеркивание!'
                )
            ),
            Optional(),
        ]
    )
    submit = SubmitField('Создать')
