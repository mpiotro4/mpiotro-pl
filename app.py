import os
import json
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, session, request, flash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

BLOG_POSTS_DIR = 'blog_posts'

translations = {
    'pl': {
        'title': 'Marcin Piotrowski - strona domowa',
        'about_me': 'O mnie',
        'about_me_content': 'Posiadam ponad 3 lata komercyjnego doświadczenia w wytwarzaniu oprogramowania z czego '
                            'dwa lata w języku Java. Większość czasu spędziłem nad pracą w dużych projektach '
                            'dotyczących ceł i podatków dla duńskiego sektora publicznego. Posiadałem szeroki zakres '
                            'obowiązków, od tworzenia testów automatycznych, implementacji nowych funkcjonalności i '
                            'wdrożeń po przygotowywanie kontraktów. Ukończyłem studia magisterskie z informatyki na '
                            'wydziale elektroniki i technik informacyjnych politechniki warszawskiej.',
        'projects': 'Projekty',
        'cv': 'CV',
        'contact': 'Kontakt',
        'blog': 'Blog',
        'my_projects': 'Lista moich projektów.',
        'my_cv': 'Moje CV.',
        'my_contact': 'Możesz się ze mną skontaktować przez e-mail: mpiotro4@outlook.com.',
        'blog_posts': 'Wpisy na blogu',
        'read_more': 'Czytaj więcej',
        'back_to_blog': 'Powrót do bloga',
        'no_posts': 'Brak wpisów na blogu.',
        'add_post': 'Dodaj wpis',
        'post_title_pl': 'Tytuł (PL)',
        'post_title_en': 'Tytuł (EN)',
        'post_content_pl': 'Treść (PL)',
        'post_content_en': 'Treść (EN)',
        'post_slug': 'Slug (URL)',
        'submit': 'Dodaj wpis',
        'post_added': 'Wpis został dodany!',
    },
    'en': {
        'title': 'Marcin Piotrowski - homepage',
        'about_me': 'About Me',
        'about_me_content': "I have over three years of commercial experience in software development, including two "
                            "years in Java. I spent most of my time working on large projects related to customs and "
                            "taxes for the Danish public sector. I had a wide range of responsibilities, "
                            "from creating automated tests and implementing new features to deployments and preparing "
                            "contracts. I hold a master's degree in computer science from the Faculty of Electronics "
                            "and Information Technology at the Warsaw University of Technology.",
        'projects': 'Projects',
        'cv': 'CV',
        'contact': 'Contact',
        'blog': 'Blog',
        'my_projects': 'List of my projects.',
        'my_cv': 'My CV.',
        'my_contact': 'You can contact me via email: mpiotro4@outlook.com.',
        'blog_posts': 'Blog posts',
        'read_more': 'Read more',
        'back_to_blog': 'Back to blog',
        'no_posts': 'No blog posts yet.',
        'add_post': 'Add post',
        'post_title_pl': 'Title (PL)',
        'post_title_en': 'Title (EN)',
        'post_content_pl': 'Content (PL)',
        'post_content_en': 'Content (EN)',
        'post_slug': 'Slug (URL)',
        'submit': 'Add post',
        'post_added': 'Post has been added!',
    }
}


def load_blog_posts():
    """Load all blog posts from JSON files."""
    posts = []
    if not os.path.exists(BLOG_POSTS_DIR):
        return posts

    for filename in os.listdir(BLOG_POSTS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(BLOG_POSTS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                post = json.load(f)
                posts.append(post)

    # Sort by date, newest first
    posts.sort(key=lambda x: x.get('date', ''), reverse=True)
    return posts


def load_blog_post(slug):
    """Load a single blog post by slug."""
    filepath = os.path.join(BLOG_POSTS_DIR, f"{slug}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_blog_post(post_data):
    """Save a blog post to a JSON file."""
    if not os.path.exists(BLOG_POSTS_DIR):
        os.makedirs(BLOG_POSTS_DIR)

    filepath = os.path.join(BLOG_POSTS_DIR, f"{post_data['slug']}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(post_data, f, ensure_ascii=False, indent=2)


@app.route('/')
def home():
    lang = session.get('lang', 'en')  # Domyślnie język polski
    return render_template('index.html', lang=lang, translations=translations[lang])

@app.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    return redirect(url_for('home'))

@app.route('/projekty')
def projekty():
    lang = session.get('lang', 'pl')
    return render_template('projects.html', lang=lang, translations=translations[lang])

@app.route('/cv')
def cv():
    lang = session.get('lang', 'pl')
    return render_template('cv.html', lang=lang, translations=translations[lang])

@app.route('/kontakt')
def kontakt():
    lang = session.get('lang', 'pl')
    return render_template('contact.html', lang=lang, translations=translations[lang])

@app.route('/blog')
def blog():
    lang = session.get('lang', 'pl')
    posts = load_blog_posts()
    return render_template('blog.html', lang=lang, translations=translations[lang], posts=posts)

@app.route('/blog/<slug>')
def blog_post(slug):
    lang = session.get('lang', 'pl')
    post = load_blog_post(slug)
    if not post:
        return "Post not found", 404
    return render_template('blog_post.html', lang=lang, translations=translations[lang], post=post)

@app.route('/blog/admin/add', methods=['GET', 'POST'])
def blog_admin():
    lang = session.get('lang', 'pl')

    if request.method == 'POST':
        slug = request.form.get('slug')
        title_pl = request.form.get('title_pl')
        title_en = request.form.get('title_en')
        content_pl = request.form.get('content_pl')
        content_en = request.form.get('content_en')

        post_data = {
            'slug': slug,
            'title': {
                'pl': title_pl,
                'en': title_en
            },
            'content': {
                'pl': content_pl,
                'en': content_en
            },
            'date': datetime.now().strftime('%Y-%m-%d'),
            'author': 'Marcin Piotrowski'
        }

        save_blog_post(post_data)
        flash(translations[lang]['post_added'])
        return redirect(url_for('blog'))

    return render_template('blog_admin.html', lang=lang, translations=translations[lang])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
