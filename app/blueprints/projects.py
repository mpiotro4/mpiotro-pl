from flask import Blueprint, render_template, session

from app.translations import translations, format_date
from app.utils import render_markdown
from app.services.project_service import get_all_projects, get_project_by_slug

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects')
def index():
    lang = session.get('lang', 'pl')
    projects = get_all_projects()

    for project in projects:
        project['date_formatted'] = format_date(project.get('date'), lang)

    return render_template('projects.html', lang=lang, translations=translations[lang], projects=projects)


@projects_bp.route('/projects/<slug>')
def project(slug):
    lang = session.get('lang', 'pl')
    p = get_project_by_slug(slug)
    if not p:
        return render_template('404.html', lang=lang, translations=translations[lang]), 404

    p['date_formatted'] = format_date(p.get('date'), lang)

    content_key = 'content_pl' if lang == 'pl' else 'content_en'
    p['html_content'] = render_markdown(p.get(content_key, ''))

    return render_template('project_post.html', lang=lang, translations=translations[lang], project=p)
