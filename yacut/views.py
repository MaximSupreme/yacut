from flask import flash, redirect, render_template, url_for

from . import app, db
from .forms import URLForm
from .models import URLMap
from .utils import generate_short_url


@app.route('/', methods=['GET', 'POST'])
def main_page():
    form = URLForm()
    if form.validate_on_submit():
        original_url = form.original_link.data
        custom_id = form.custom_id.data
        if custom_id:
            if URLMap.query.filter_by(short=custom_id).first():
                flash(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
                return render_template('base.html', form=form)
            short_id = custom_id
        else:
            short_id = generate_short_url()
        url_map = URLMap(
            original=original_url, short=short_id
        )
        db.session.add(url_map)
        db.session.commit()
        short_url = url_for(
            'redirect_to_original', short_id=short_id, _external=True
        )
        flash(
            f'Ваша новая ссылка: <a href="{short_url}">{short_url}</a>',
        )
    for field, errors in form.errors.items():
        for error in errors:
            flash(
                f'Ошибка в поле {getattr(form, field).label.text}: {error}',
            )
    return render_template('index.html', form=form)


@app.route('/<short_id>')
def redirect_to_original(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
