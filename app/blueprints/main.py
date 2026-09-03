from flask import Blueprint, render_template
from app.translations import translations

main_bp = Blueprint('main', __name__)


@main_bp.route('/', defaults={'lang': 'en'})
@main_bp.route('/pl/', defaults={'lang': 'pl'})
def index(lang):
    return render_template('index.html', lang=lang, translations=translations[lang])
