from flask import Blueprint, render_template, session

from app.translations import translations, format_date
from app.utils import render_markdown
from app.services.blog_service import get_all_posts, get_post_by_slug

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/blog')
def index():
    """Blog homepage - list of all posts"""
    lang = session.get('lang', 'pl')
    posts = get_all_posts()

    # Format dates for all posts
    for post in posts:
        post['date_formatted'] = format_date(post.get('date'), lang)
        post['updated_formatted'] = format_date(post.get('updated'), lang) if post.get('updated') else None

    return render_template('blog.html', lang=lang, translations=translations[lang], posts=posts)


@blog_bp.route('/blog/<slug>')
def post(slug):
    """Single blog post"""
    lang = session.get('lang', 'pl')
    post = get_post_by_slug(slug)
    if not post:
        return render_template('404.html', lang=lang, translations=translations[lang]), 404

    # Format dates for display
    post['date_formatted'] = format_date(post.get('date'), lang)
    post['updated_formatted'] = format_date(post.get('updated'), lang) if post.get('updated') else None

    # Convert markdown content to HTML (use appropriate language)
    content_key = 'content_pl' if lang == 'pl' else 'content_en'
    post['html_content'] = render_markdown(post.get(content_key, ''))

    return render_template('blog_post.html', lang=lang, translations=translations[lang], post=post)
