import os
import re
from datetime import datetime

import markdown
import yaml
from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

BLOG_DIR = 'blog'

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
    }
}


def parse_markdown_post(content):
    """Parse markdown file with YAML frontmatter and language sections."""
    # Split frontmatter and content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None

    # Parse YAML frontmatter
    try:
        metadata = yaml.safe_load(parts[1])
    except:
        return None

    # Get content after frontmatter
    post_content = parts[2].strip()

    # Split content by language markers [PL] and [EN]
    pl_match = re.search(r'\[PL\](.*?)(?=\[EN\]|$)', post_content, re.DOTALL)
    en_match = re.search(r'\[EN\](.*?)$', post_content, re.DOTALL)

    content_pl = pl_match.group(1).strip() if pl_match else ''
    content_en = en_match.group(1).strip() if en_match else ''

    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'nl2br'])
    content_pl_html = md.convert(content_pl) if content_pl else ''
    md.reset()
    content_en_html = md.convert(content_en) if content_en else ''

    return {
        'slug': metadata.get('slug', ''),
        'title': {
            'pl': metadata.get('title_pl', ''),
            'en': metadata.get('title_en', '')
        },
        'content': {
            'pl': content_pl_html,
            'en': content_en_html
        },
        'date': metadata.get('date', ''),
        'author': metadata.get('author', 'Marcin Piotrowski')
    }


def load_blog_posts():
    """Load all blog posts from Markdown files."""
    posts = []
    if not os.path.exists(BLOG_DIR):
        return posts

    for filename in os.listdir(BLOG_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(BLOG_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                post = parse_markdown_post(content)
                if post:
                    posts.append(post)

    # Sort by date, newest first
    posts.sort(key=lambda x: x.get('date', ''), reverse=True)
    return posts


def load_blog_post(slug):
    """Load a single blog post by slug."""
    filepath = os.path.join(BLOG_DIR, f"{slug}.md")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return parse_markdown_post(content)
    return None


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
