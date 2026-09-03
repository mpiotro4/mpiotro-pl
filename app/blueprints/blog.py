from flask import Blueprint, render_template, url_for, abort

from app.translations import translations, format_date
from app.utils import render_markdown
from app.services.blog_service import get_all_posts, get_post_by_slug

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/blog/', defaults={'lang': 'en'})
@blog_bp.route('/pl/blog/', defaults={'lang': 'pl'})
def index(lang):
    """Blog homepage - list of all posts"""
    posts = get_all_posts()

    for post in posts:
        post['date_formatted'] = format_date(post.get('date'), lang)
        post['updated_formatted'] = format_date(post.get('updated'), lang) if post.get('updated') else None

    return render_template(
        'post_list.html',
        lang=lang,
        translations=translations[lang],
        items=posts,
        item_endpoint='blog.post',
        section_title=translations[lang]['blog'],
        empty_message=translations[lang]['no_posts'],
    )


@blog_bp.route('/blog/<slug>/', defaults={'lang': 'en'})
@blog_bp.route('/pl/blog/<slug>/', defaults={'lang': 'pl'})
def post(lang, slug):
    """Single blog post"""
    post = get_post_by_slug(slug)
    if not post:
        abort(404)

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
