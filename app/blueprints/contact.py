from flask import Blueprint, render_template, session
from app.translations import translations, DEFAULT_LANGUAGE

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/contact')
def index():
    lang = session.get('lang', DEFAULT_LANGUAGE)
    return render_template('contact.html', lang=lang, translations=translations[lang])
