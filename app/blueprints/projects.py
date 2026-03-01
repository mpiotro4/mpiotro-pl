from flask import Blueprint, render_template, session, url_for

from app.translations import translations, format_date, DEFAULT_LANGUAGE
from app.utils import render_markdown
from app.services.project_service import get_all_projects, get_project_by_slug

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects')
def index():
    lang = session.get('lang', DEFAULT_LANGUAGE)
    projects = get_all_projects()

    for project in projects:
        project['date_formatted'] = format_date(project.get('date'), lang)

    return render_template(
        'post_list.html',
        lang=lang,
        translations=translations[lang],
        items=projects,
        item_endpoint='projects.project',
        section_title=translations[lang]['projects'],
        empty_message=translations[lang]['no_projects'],
    )


@projects_bp.route('/projects/<slug>')
def project(slug):
    lang = session.get('lang', DEFAULT_LANGUAGE)
    p = get_project_by_slug(slug)
    if not p:
        return render_template('404.html'), 404

    p['date_formatted'] = format_date(p.get('date'), lang)

    content_key = 'content_pl' if lang == 'pl' else 'content_en'
    p['html_content'] = render_markdown(p.get(content_key, ''))

    return render_template(
        'post_detail.html',
        lang=lang,
        translations=translations[lang],
        item=p,
        index_url=url_for('projects.index'),
        back_label=translations[lang]['back_to_projects'],
    )
