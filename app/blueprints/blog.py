from flask import Blueprint, render_template, session, url_for

from app.translations import translations, format_date
from app.utils import render_markdown
from app.services.blog_service import get_all_posts, get_post_by_slug

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/blog')
def index():
    """Blog homepage - list of all posts"""
    lang = session.get('lang', 'pl')
    posts = get_all_posts()

    for post in posts:
        post['date_formatted'] = format_date(post.get('date'), lang)
        post['updated_formatted'] = format_date(post.get('updated'), lang) if post.get('updated') else None

    return render_template(
        'post_list.html',
        lang=lang,
        translations=translations[lang],
        items=posts,
        base_url='/blog',
        section_title=translations[lang]['blog'],
        empty_message=translations[lang]['no_posts'],
    )


@blog_bp.route('/blog/<slug>')
def post(slug):
    """Single blog post"""
    lang = session.get('lang', 'pl')
    post = get_post_by_slug(slug)
    if not post:
        return render_template('404.html', lang=lang, translations=translations[lang]), 404

    post['date_formatted'] = format_date(post.get('date'), lang)
    post['updated_formatted'] = format_date(post.get('updated'), lang) if post.get('updated') else None

    content_key = 'content_pl' if lang == 'pl' else 'content_en'
    post['html_content'] = render_markdown(post.get(content_key, ''))

    return render_template(
        'post_detail.html',
        lang=lang,
        translations=translations[lang],
        item=post,
        index_url=url_for('blog.index'),
        back_label=translations[lang]['back_to_blog'],
    )
