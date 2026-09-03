from flask import Blueprint, render_template
from app.translations import translations

main_bp = Blueprint('main', __name__)


@main_bp.route('/', defaults={'lang': 'pl'})
@main_bp.route('/en/', defaults={'lang': 'en'})
def index(lang):
    return render_template('index.html', lang=lang, translations=translations[lang])
