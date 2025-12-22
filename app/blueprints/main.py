from flask import Blueprint, render_template, session, redirect, url_for, request
from app.translations import translations

main_bp = Blueprint('main', __name__)


@main_bp.route('/about')
def about():
    lang = session.get('lang', 'en')
    return render_template('index.html', lang=lang, translations=translations[lang])


@main_bp.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    # Redirect to the previous page, or home if no referrer
    return redirect(request.referrer or url_for('blog.index'))
