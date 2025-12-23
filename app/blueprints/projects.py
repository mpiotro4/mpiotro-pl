from flask import Blueprint, render_template, session, abort
import markdown
from app.translations import translations
from app.services.projects_service import get_all_projects, get_project_by_slug, get_projects_by_year

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects')
def index():
    lang = session.get('lang', 'pl')
    projects_by_year = get_projects_by_year()
    return render_template('projects.html', lang=lang, translations=translations[lang],
                         projects_by_year=projects_by_year)


@projects_bp.route('/projects/<slug>')
def project(slug):
    lang = session.get('lang', 'pl')
    project = get_project_by_slug(slug)

    if not project:
        abort(404)

    # Convert markdown to HTML
    content_text = project['content_pl'] if lang == 'pl' else project['content_en']
    html_content = markdown.markdown(
        content_text,
        extensions=['tables', 'fenced_code', 'codehilite', 'nl2br'],
        extension_configs={
            'codehilite': {
                'guess_lang': False,
                'use_pygments': False,
                'noclasses': True
            }
        }
    )

    return render_template('project.html', lang=lang, translations=translations[lang],
                         project=project, content=html_content)
