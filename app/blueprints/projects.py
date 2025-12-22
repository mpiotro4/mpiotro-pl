from flask import Blueprint, render_template, session
from app.translations import translations
from app.projects_data import PROJECTS

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects')
def index():
    lang = session.get('lang', 'en')
    return render_template('projects.html', lang=lang, translations=translations[lang], projects=PROJECTS)
