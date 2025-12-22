import os
from flask import Flask, render_template, redirect, url_for, session, request
import markdown

from translations import translations, format_date
from blog_utils import get_all_posts, get_post_by_slug
from projects_data import PROJECTS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')


@app.route('/')
def home():
    lang = session.get('lang', 'pl')
    posts = get_all_posts()

    # Format dates for all posts
    for post in posts:
        post['date_formatted'] = format_date(post.get('date'), lang)
        post['updated_formatted'] = format_date(post.get('updated'), lang) if post.get('updated') else None

    return render_template('blog.html', lang=lang, translations=translations[lang], posts=posts)

@app.route('/about')
def about():
    lang = session.get('lang', 'en')
    return render_template('index.html', lang=lang, translations=translations[lang])

@app.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    # Redirect to the previous page, or home if no referrer
    return redirect(request.referrer or url_for('home'))


@app.route('/projects')
def projects():
    lang = session.get('lang', 'en')
    return render_template('projects.html', lang=lang, translations=translations[lang], projects=PROJECTS)

@app.route('/contact')
def contact():
    lang = session.get('lang', 'en')
    return render_template('contact.html', lang=lang, translations=translations[lang])

@app.route('/blog/<slug>')
def blog_post(slug):
    lang = session.get('lang', 'pl')
    post = get_post_by_slug(slug)
    if not post:
        return render_template('404.html', lang=lang, translations=translations[lang]), 404

    # Format dates for display
    post['date_formatted'] = format_date(post.get('date'), lang)
    post['updated_formatted'] = format_date(post.get('updated'), lang) if post.get('updated') else None

    # Convert markdown content to HTML (use appropriate language)
    content_key = 'content_pl' if lang == 'pl' else 'content_en'
    content_text = post.get(content_key, '')
    html_content = markdown.markdown(
        content_text,
        extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'nl2br'
        ],
        extension_configs={
            'codehilite': {
                'guess_lang': False,
                'use_pygments': False,
                'noclasses': True
            }
        }
    )
    post['html_content'] = html_content

    return render_template('blog_post.html', lang=lang, translations=translations[lang], post=post)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
